# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import expression
from odoo.tools import float_compare, float_is_zero


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    order_type = fields.Selection(
        related="order_id.order_type",
        store=True,
        precompute=True,
        readonly=True,
    )
    blanket_move_ids = fields.One2many(
        "stock.move",
        "call_off_sale_line_id",
        string="Stock Moves on Blanket Order",
    )
    blanket_line_id = fields.Many2one(
        "sale.order.line",
        string="Blanket Order Line",
        help="The blanket order line corresponding to this call-off order line.",
        index="btree_not_null",
    )
    call_off_line_ids = fields.One2many(
        "sale.order.line",
        "blanket_line_id",
        string="Call-off Order Lines",
        help="The call-off order lines linked to this blanket order line.",
    )
    call_off_remaining_qty = fields.Float(
        string="Quantity remaining for Call-off",
        compute="_compute_call_off_remaining_qty",
        store=True,
        help="The quantity remaining to consume by call-off orders in case "
        "of a blanket order. This quantity is the difference between the quantity "
        "not yet delivered or part of a pending delivery and the ordered quantity.",
    )
    blanket_validity_start_date = fields.Date(
        string="Validity Start Date",
        related="order_id.blanket_validity_start_date",
        readonly=True,
        store=True,
        copy=False,
        precompute=True,
    )
    blanket_validity_end_date = fields.Date(
        string="Validity End Date",
        related="order_id.blanket_validity_end_date",
        readonly=True,
        store=True,
        copy=False,
        precompute=True,
    )
    blanket_order_id = fields.Many2one(
        "sale.order",
        related="order_id.blanket_order_id",
        readonly=True,
        store=True,
        copy=False,
        precompute=True,
    )

    def init(self):
        self._cr.execute(
            """
            CREATE INDEX IF NOT EXISTS
                ale_order_line_blanket_validity_range_index
            ON
                sale_order_line
            USING
                gist (daterange(blanket_validity_start_date, blanket_validity_end_date, '[]'))
            WHERE
                blanket_validity_end_date IS NOT NULL
                AND blanket_validity_start_date IS NOT NULL
            """
        )

    @api.constrains(
        "state",
        "blanket_order_id",
        "order_type",
        "product_id",
        "product_uom_qty",
        "display_type",
    )
    def _check_call_off_order_line(self):
        """Check the constraints for call-off order lines.

        The constraints are:
        - The product must be part of the linked blanket order.
        - The quantity to procure must be less than or equal to the quantity
          remaining to deliver in the linked blanket order for this product.
        """
        matching_dict = self._get_blanket_lines_for_call_off_lines_dict()
        for call_of_lines, blanket_lines in matching_dict.values():
            if not blanket_lines:
                line = call_of_lines[0]
                raise ValidationError(
                    _(
                        "The product is not part of linked blanket order. "
                        "(Product: '%(product)s', Order: '%(order)s', "
                        "Blanket Order: '%(blanket_order)s')",
                        product=line.product_id.display_name,
                        order=line.order_id.name,
                        blanket_order=line.blanket_order_id.name,
                    )
                )

            qty_remaining_to_procure = sum(
                blanket_lines.mapped("call_off_remaining_qty")
            )
            qty_to_procure = sum(call_of_lines.mapped("qty_to_deliver"))
            if (
                float_compare(
                    qty_to_procure,
                    qty_remaining_to_procure,
                    precision_rounding=call_of_lines[0].product_uom.rounding,
                )
                > 0
            ):
                raise ValidationError(
                    _(
                        "The quantity to procure is greater than the quantity "
                        "remaining to deliver in the linked blanket order for "
                        "this product. (Product: '%(product)s', Order: "
                        "'%(order)s', Blanket Order: '%(blanket_order)s')",
                        product=call_of_lines[0].product_id.display_name,
                        order=call_of_lines[0].order_id.name,
                        blanket_order=call_of_lines[0].blanket_order_id.name,
                    )
                )

    @api.constrains("order_type", "price_unit")
    def _check_call_off_order_line_price(self):
        price_precision = self.env["decimal.precision"].precision_get("Product Price")
        for line in self:
            if line.order_type == "call_off" and not float_is_zero(
                line.price_unit, precision_digits=price_precision
            ):
                raise ValidationError(
                    _(
                        "The price of a call-off order line must be 0.0. "
                        "(Order: '%(order)s', Product: '%(product)s')",
                        order=line.order_id.name,
                        product=line.product_id.display_name,
                    )
                )

    @api.constrains(
        "blanket_validity_start_date",
        "blanket_validity_end_date",
        "product_id",
    )
    def _check_blanket_product_not_overlapping(self):
        """We check that a product is not part of multiple blanket orders
        with overlapping validity periods.

        This constraint is only applied to blanket order lines.

        The constraint is:
        - A product cannot be part of multiple blanket orders with overlapping
            validity periods.
        - The constraint is checked for all blanket order lines of the same product
            as the current line.
        - We exclude lines with no quantity remaining to procure since a new order could
            be created with the same product to cover a new need.
        """
        self.flush_model()
        for rec in self:
            order = rec.order_id
            if (
                order.order_type != "blanket"
                or not rec.blanket_validity_start_date
                or not rec.blanket_validity_end_date
            ):
                continue
            # here we use a plain SQL query to benefit of the daterange
            # function available in PostgresSQL
            # (http://www.postgresql.org/docs/current/static/rangetypes.html)
            sql = """
                SELECT
                    sol.id
                FROM
                    sale_order_line sol
                WHERE
                    sol.blanket_validity_start_date is not null
                    AND sol.blanket_validity_end_date is not null
                    AND DATERANGE(
                        sol.blanket_validity_start_date,
                        sol.blanket_validity_end_date,
                        '[]'
                    ) && DATERANGE(
                        %s::date,
                         %s::date,
                         '[]'
                    )
                """
            domain = [
                ("call_off_remaining_qty", ">", 0),
                ("order_id", "!=", order.id),
                ("state", "not in", ["done", "cancel"]),
                ("order_type", "=", "blanket"),
            ]
            for (
                matching_field
            ) in self._get_call_off_line_to_blanked_line_matching_fields():
                value = rec[matching_field]
                if isinstance(value, models.BaseModel):
                    value = value.id
                domain.append((matching_field, "=", value))
            _t, where, matching_field_values = expression(
                domain, self, alias="sol"
            ).query.get_sql()
            sql += f"AND {where}"
            self.env.cr.execute(
                sql,
                (
                    rec.blanket_validity_start_date,
                    rec.blanket_validity_end_date,
                    *matching_field_values,
                ),
            )
            res = self.env.cr.fetchall()
            if res:
                sol = self.browse(res[0][0])
                raise ValidationError(
                    _(
                        "The product '%(product_name)s' is already part of another "
                        "blanket order %(order_name)s.",
                        product_name=sol.product_id.name,
                        order_name=sol.order_id.name,
                    )
                )

    @api.depends("call_off_line_ids", "order_type", "call_off_line_ids.state")
    def _compute_call_off_remaining_qty(self):
        """Compute the quantity remaining to deliver for call-off order lines.

        This value is only relevant on blanket order lines. It's used to know how much
        quantity is still available to deliver by a call-off order lines.
        """
        self.flush_model()
        blanket_lines = self.filtered(lambda l: l.order_type == "blanket")
        res = self.read_group(
            [("blanket_line_id", "in", blanket_lines.ids), ("state", "!=", "cancel")],
            ["blanket_line_id", "product_uom_qty:sum"],
            ["blanket_line_id"],
            orderby="blanket_line_id.id",
        )
        call_off_delivered_qty = {}
        for r in res:
            call_off_delivered_qty[r["blanket_line_id"][0]] = r["product_uom_qty"]
        for line in self:
            new_call_off_remaining_qty = call_off_delivered_qty.get(line.id, 0.0)
            if line in blanket_lines:
                new_call_off_remaining_qty = (
                    line.product_uom_qty - new_call_off_remaining_qty
                )
            if float_compare(
                new_call_off_remaining_qty,
                line.call_off_remaining_qty,
                precision_rounding=line.product_uom.rounding or 1.0,
            ):
                line.call_off_remaining_qty = new_call_off_remaining_qty

    def _get_call_off_line_to_blanked_line_matching_fields(self):
        return ["product_id", "product_packaging_id", "order_partner_id"]

    def _get_blanket_lines_for_call_off_lines_dict(self):
        """Get the matching blanket order lines for the call-off order lines.

        see `_match_lines_to_blanket` for more details.
        """
        call_off_lines = self.filtered(lambda l: l.order_type == "call_off")
        blanket_lines = self.blanket_order_id.order_line
        return self._match_lines_to_blanket(call_off_lines, blanket_lines)

    def _to_blanket_line_matching_key(self):
        """Compute the matching key for the blanket order line.

        The key is a tuple of the fields provided by the method
        `_get_call_off_line_to_blanked_line_matching_fields`.

        :return: A tuple of the matching fields.
        """
        return (
            *[
                self[field]
                for field in self._get_call_off_line_to_blanked_line_matching_fields()
            ],
        )

    @api.model
    def _match_lines_to_blanket(self, order_lines, blanket_lines):
        """Compute the matching between given order lines and the blanket order lines.

        The matching is done on the fields provided by the method
        `_get_call_off_line_to_blanked_line_matching_fields`.

        :return: A dictionary. The keys are tuples of the matching fields and the
            blanket order id. The values are tuples of the call-off order lines and
            the matching blanket order lines.

        """
        call_off_lines_by_key = defaultdict(lambda: self.env["sale.order.line"])
        for line in order_lines:
            if line.display_type:
                continue
            if line.state == "cancel":
                continue
            key = line._to_blanket_line_matching_key()
            call_off_lines_by_key[key] |= line

        blanket_lines_by_key = defaultdict(lambda: self.env["sale.order.line"])
        for line in blanket_lines:
            if (
                float_compare(
                    line.call_off_remaining_qty,
                    0.0,
                    precision_rounding=line.product_uom.rounding,
                )
                <= 0
            ):
                continue
            key = line._to_blanket_line_matching_key()
            blanket_lines_by_key[key] |= line

        return {
            key: (call_off_lines_by_key[key], blanket_lines_by_key.get(key))
            for key in call_off_lines_by_key.keys()
        }

    def _prepare_reserve_procurement_values(self, group_id=None):
        if self.order_type == "blanket":
            return self._prepare_reserve_procurement_values_blanket(group_id)
        else:
            return super()._prepare_reserve_procurement_values(group_id)

    def _prepare_reserve_procurement_values_blanket(self, group_id=None):
        """Prepare the values for the procurement to reserve the stock for a
        blanket order line.

        In the case of a blanket order, the procurement date_planned and date_deadline
        should be set to the validity start date of the blanket order. This is because
        the stock should be reserved for the blanket order at the start of the validity
        period, not at the time of the call-off order.
        """
        values = super()._prepare_reserve_procurement_values(group_id)
        values["date_planned"] = self.blanket_validity_start_date
        values["date_deadline"] = self.blanket_validity_start_date
        return values

    def _get_display_price(self):
        if self.order_type == "call_off":
            return 0.0
        return super()._get_display_price()

    def _prepare_procurement_values(self, group_id=False):
        res = super()._prepare_procurement_values(group_id=group_id)
        call_off_sale_line_id = self.env.context.get("call_off_sale_line_id")
        res["call_off_sale_line_id"] = call_off_sale_line_id
        return res

    def _compute_qty_at_date(self):
        # Overload to consider the call-off order lines in the computation
        # For these lines we take the values computed on the corresponding
        # blanket order line
        call_off_lines = self.filtered(lambda l: l.order_type == "call_off")
        other_lines = self - call_off_lines
        res = super(SaleOrderLine, other_lines)._compute_qty_at_date()
        for line in call_off_lines:
            blanket_line = fields.first(
                line.blanket_order_id.order_line.filtered(
                    lambda l: l.product_id == line.product_id
                )
            )
            line.virtual_available_at_date = blanket_line.virtual_available_at_date
            line.scheduled_date = blanket_line.scheduled_date
            line.forecast_expected_date = blanket_line.forecast_expected_date
            line.free_qty_today = blanket_line.free_qty_today
            line.qty_available_today = blanket_line.qty_available_today
        return res

    def _compute_qty_to_deliver(self):
        # Overload to consider the call-off order lines in the computation
        # For these lines the qty to deliver is the same as the product_uom_qty
        # while the order is not confirmed or done. Otherwise it is 0 as the
        # delivery is done on the blanket order line.
        call_off_lines = self.filtered(lambda l: l.order_type == "call_off")
        other_lines = self - call_off_lines
        res = super(SaleOrderLine, other_lines)._compute_qty_to_deliver()
        for line in call_off_lines:
            if line.state in ("sale", "done", "cancel"):
                line.display_qty_widget = False
                line.qty_to_deliver = 0.0
            else:
                line.display_qty_widget = True
                line.qty_to_deliver = self.product_uom_qty
        return res

    def _compute_qty_delivered(self):
        # Overload to consider the call-off order lines in the computation
        # For these lines the qty delivered is always 0 as the delivery is
        # done on the blanket order line.
        call_off_lines = self.filtered(lambda l: l.order_type == "call_off")
        other_lines = self - call_off_lines
        res = super(SaleOrderLine, other_lines)._compute_qty_delivered()
        for line in call_off_lines:
            line.qty_delivered = 0
        return res

    def _compute_qty_to_invoice(self):
        # Overload to consider the call-off order lines in the computation
        # For these lines the qty to invoice is always 0 as the invoicing is
        # done on the blanket order line.
        call_off_lines = self.filtered(lambda l: l.order_type == "call_off")
        other_lines = self - call_off_lines
        res = super(SaleOrderLine, other_lines)._compute_qty_to_invoice()
        for line in call_off_lines:
            line.qty_to_invoice = 0
        return res

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        # Overload to consider the call-off order lines in the computation
        # The launch of the stock rule is done on the blanket order lines.
        # In case of multiple lines for the same product, we must ensure that
        # the stock rule is launched on a single blanket order line for the
        # quantity still to deliver on this line.
        # We must also take care of the reservation strategy of the blanket order.
        call_off_lines = self.browse()
        if not self.env.context.get("disable_call_off_stock_rule"):
            call_off_lines = self.filtered(lambda l: l.order_type == "call_off")
        other_lines = self - call_off_lines
        res = super(SaleOrderLine, other_lines)._action_launch_stock_rule(
            previous_product_uom_qty
        )
        if not self.env.context.get("call_off_split_process"):
            # When splitting a call-off line, we don't want to launch the stock rule
            # since it will be done after the split process
            call_off_lines._launch_stock_rule_on_blanket_order(previous_product_uom_qty)
        return res

    def _link_to_blanket_order_line(self):
        """Link the call-off order lines to the corresponding blanket order lines.

        This method is called at the confirmation time of call-off orders. It will
        link each call-off line to the corresponding blanket line. If the quantity on
        the call-off line is greater than the quantity on the blanket line, the
        call-off line will be split to ensure taht the quantity on the call-off line
        is less than or equal to the quantity on the referenced blanket line. The split
        process is special case which only occurs when multiple lines into for a same
        product and package exists in the blanket order.
        """
        matching_dict = self._get_blanket_lines_for_call_off_lines_dict()
        for call_off_lines, blanket_lines in matching_dict.values():
            for call_off_line in call_off_lines:
                if call_off_line.blanket_line_id:
                    continue
                qty_to_deliver = call_off_line.product_uom_qty
                for blanket_line in blanket_lines:
                    # All the call-off quantities can be delivered on this blanket line
                    if (
                        float_compare(
                            qty_to_deliver,
                            blanket_line.call_off_remaining_qty,
                            precision_rounding=blanket_line.product_uom.rounding,
                        )
                        <= 0
                    ):
                        call_off_line.blanket_line_id = blanket_line
                        qty_to_deliver = 0
                        break
                    # The quantity to deliver is greater than the remaining quantity
                    # on this blanket line. We split the call-off line into a new line
                    # which will consume the remaining quantity on this blanket line.
                    # The remaining quantity will be consumed by the next blanket line.
                    qty_deliverable = blanket_line.call_off_remaining_qty
                    if not float_is_zero(
                        qty_deliverable,
                        precision_rounding=call_off_line.product_uom.rounding,
                    ):
                        call_off_line = call_off_line.with_context(
                            call_off_split_process=True
                        )
                        qty_to_deliver -= qty_deliverable
                        call_off_line.product_uom_qty -= qty_deliverable
                        # we force the state to draft to avoid the launch of the stock
                        # rule at copy
                        new_call_off_line = call_off_line.copy(
                            default={
                                "product_uom_qty": qty_deliverable,
                                "order_id": call_off_line.order_id.id,
                            }
                        )
                        new_call_off_line.blanket_line_id = blanket_line
                        new_call_off_line.state = call_off_line.state
                if not float_is_zero(
                    qty_to_deliver,
                    precision_rounding=call_off_line.product_uom.rounding,
                ):
                    raise ValueError(
                        "The quantity to deliver on the call-off order line "
                        "is greater than the quantity remaining to deliver on "
                        "the blanket order line."
                    )

    def _launch_stock_rule_on_blanket_order(self, previous_product_uom_qty):
        for line in self:
            line = line.with_context(call_off_sale_line_id=line.id)
            blanket_order = line.blanket_order_id
            if not blanket_order:
                raise ValueError("A call-off order must have a blanket order.")
            if blanket_order.blanket_reservation_strategy == "at_call_off":
                line._stock_rule_on_blanket_with_reservation_at_call_off(
                    previous_product_uom_qty
                )
            else:
                raise ValueError("Invalid blanket reservation strategy.")

    def _stock_rule_on_blanket_with_reservation_at_call_off(
        self, previous_product_uom_qty
    ):
        """In case of a blanket order with reservation at call-off, we must cancel
        the existing reservation, launch the stock rule on the blanket order lines
        for the quantity to deliver and create a new reservation for the remaining
        quantity.
        """
        self.ensure_one()
        qty_to_deliver = self.product_uom_qty
        blanket_line = self.blanket_line_id
        old_state = blanket_line.state
        if old_state == "done":
            # We must unlock the line to manually deliver the quantity
            blanket_line.state = "sale"
        wizard = (
            self.env["manual.delivery"]
            .with_context(
                active_id=blanket_line.id,
                active_model="sale.order.line",
                active_ids=blanket_line.ids,
            )
            .create({})
        )
        wizard.line_ids.quantity = qty_to_deliver
        wizard.confirm()
        if old_state == "done":
            blanket_line.state = "done"
