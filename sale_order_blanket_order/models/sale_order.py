# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.osv.expression import FALSE_DOMAIN
from odoo.tools import float_compare

from odoo.addons.sale.models.sale_order import READONLY_FIELD_STATES


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_type = fields.Selection(
        [
            ("order", "Order"),
            ("blanket", "Blanket Order"),
            ("call_off", "Call-off Order"),
        ],
        default="order",
        required=True,
        help="Specifies the type of sale order: Order, Blanket, or Call-off.",
        states=READONLY_FIELD_STATES,
        index=True,
    )
    blanket_order_id = fields.Many2one(
        "sale.order",
        string="Blanket Order",
        help="The blanket order that this call-off order is related to.",
        states=READONLY_FIELD_STATES,
        index="btree_not_null",
    )
    blanket_order_id_domain = fields.Binary(
        string="Blanket Order Domain",
        compute="_compute_blanket_order_id_domain",
        help="The domain to search for the blanket order candidates.",
    )
    call_off_order_ids = fields.One2many(
        "sale.order",
        "blanket_order_id",
        string="Call-off Orders",
        help="The call-off orders related to this blanket order.",
    )
    call_off_order_count = fields.Integer(
        compute="_compute_call_off_order_count",
        string="Call-off Order Count",
        help="The number of call-off orders related to this blanket order.",
    )
    blanket_validity_start_date = fields.Date(
        string="Validity Start Date",
        help="The start date of the validity period for the blanket order.",
    )
    blanket_validity_end_date = fields.Date(
        string="Validity End Date",
        help="The end date of the validity period for the blanket order.",
    )
    blanket_reservation_strategy = fields.Selection(
        [
            ("at_call_off", "At Call-off"),
        ],
        string="Reservation Strategy",
        compute="_compute_blanket_reservation_strategy",
        readonly=False,
        help="Specifies when the stock should be reserved for the blanket order. "
        " When the strategy is 'At Order Confirmation', the stock is reserved "
        "when the blanket order is confirmed. When the strategy is 'At Call-off', "
        "the stock is reserved when the call-off order is confirmed.",
        store=True,
        precompute=True,
    )
    is_blanket_reservation_strategy_editable = fields.Boolean(
        compute="_compute_is_blanket_reservation_strategy_editable",
        help="Indicates if the reservation strategy can be edited.",
    )
    blanket_eol_strategy = fields.Selection(
        [
            ("deliver", "Deliver Remaining Quantity"),
        ],
        help="Specifies the end-of-life strategy for the blanket order. At the end "
        "of the validity period, in any case if a reserved quantity remains, the "
        "system will release the reservation. If the strategy is 'Deliver "
        "Remaining Quantity', the system will automaticaly create a delivery order "
        "for the remaining quantity.",
    )
    is_blanket_eol_strategy_editable = fields.Boolean(
        compute="_compute_is_blanket_eol_strategy_editable",
        help="Indicates if the end-of-life strategy can be edited. By default, the "
        "end-of-life strategy can be edited while the blanket order is not finalized.",
    )
    blanket_need_to_be_finalized = fields.Boolean(
        string="Need to be Finalized",
        help="Indicates if the blanket order needs to be finalized. This field is "
        "a technical field used to manage the end-of-life of the blanket orders. "
        "To avoid costly operations to determine if the blanket order needs to be "
        "finalized once the validity period is reached, the system will set this "
        "field to True when a blanket order is confirmed. To know if a blanket "
        "order needs to be finalized, the system will search for the blanket "
        "orders with this field set to True and the validity period reached."
        "Once the blanket order is finalized, the system will set this field to "
        "False. In this way, the DB will always contain less records to search "
        "with this field set to True.",
        default=False,
    )

    create_call_off_from_so_if_possible = fields.Boolean(
        default=lambda self: self.env.company.create_call_off_from_so_if_possible,
        help="When this option is enabled, the system will automatically create "
        "call-off orders when a sales order is confirmed and some lines refer to a "
        "blanket order.",
        states=READONLY_FIELD_STATES,
    )

    def init(self):
        self._cr.execute(
            """
            CREATE INDEX IF NOT EXISTS
                sale_order_blanket_order_to_finalize_index
            ON
                sale_order (blanket_need_to_be_finalized)
            WHERE
                blanket_need_to_be_finalized IS TRUE;
        """
        )

    @api.constrains("order_type", "blanket_order_id", "state")
    def _check_order_type(self):
        for order in self:
            if order.state != "sale":
                continue
            if order.order_type == "blanket" and order.blanket_order_id:
                raise ValidationError(_("A blanket order cannot have a blanket order."))
            if (
                order.order_type == "call_off"
                and order.blanket_order_id.order_type != "blanket"
            ):
                raise ValidationError(_("A call-off order must have a blanket order."))
            if order.order_type == "order" and order.blanket_order_id:
                raise ValidationError(_("An order cannot have a blanket order."))

    @api.constrains(
        "order_type",
        "blanket_validity_start_date",
        "blanket_validity_end_date",
        "state",
    )
    def _check_validity_dates(self):
        for order in self:
            if order.state != "sale":
                continue
            if order.order_type == "blanket":
                if not order.blanket_validity_start_date:
                    raise ValidationError(
                        _("The validity start date is required for a blanket order.")
                    )
                if not order.blanket_validity_end_date:
                    raise ValidationError(
                        _("The validity end date is required for a blanket order.")
                    )
                if order.blanket_validity_end_date < order.blanket_validity_start_date:
                    raise ValidationError(
                        _(
                            "The validity end date must be greater than the "
                            "validity start date."
                        )
                    )

    @api.constrains(
        "order_type", "blanket_order_id", "date_order", "commitment_date", "state"
    )
    def _check_call_of_link_to_valid_blanket(self):
        for rec in self:
            if rec.state != "sale":
                continue
            if (
                rec.order_type != "call_off"
                or not rec.date_order
                or rec.blanket_order_id.order_type != "blanket"
                or rec.blanket_order_id.state not in ("sale", "done")
            ):
                continue
            expected_delivery_date = rec.commitment_date or rec.date_order
            if isinstance(expected_delivery_date, datetime):
                expected_delivery_date = expected_delivery_date.date()
            if (
                expected_delivery_date
                < rec.blanket_order_id.blanket_validity_start_date
                or expected_delivery_date
                > rec.blanket_order_id.blanket_validity_end_date
            ):
                raise ValidationError(
                    _(
                        "The call-off order must be within the validity period of "
                        "the blanket order."
                    )
                )

    @api.constrains("order_type", "blanket_order_id", "state")
    def _check_blanket_order_state(self):
        for order in self:
            if order.state != "sale":
                continue
            if (
                order.order_type != "call_off"
                or not order.blanket_order_id
                or order.blanket_order_id.order_type != "blanket"
            ):
                continue
            if order.order_type == "call_off" and order.blanket_order_id.state not in (
                "sale",
                "done",
            ):
                raise ValidationError(
                    _(
                        "The blanket order must be confirmed before creating a call-off order."
                    )
                )

    @api.depends("order_type", "commitment_date", "partner_id")
    def _compute_blanket_order_id_domain(self):
        for order in self:
            if order.order_type == "call_off" and self.partner_id:
                domain = order._get_single_blanket_order_candidates_domain()
            else:
                domain = FALSE_DOMAIN

            order.blanket_order_id_domain = domain

    @api.depends("order_type", "state", "blanket_reservation_strategy")
    def _compute_blanket_reservation_strategy(self):
        for order in self:
            if order.state != "draft":
                continue
            if order.order_type == "blanket" and not order.blanket_reservation_strategy:
                order.blanket_reservation_strategy = "at_call_off"

    @api.depends("call_off_order_ids")
    def _compute_call_off_order_count(self):
        if not any(self.call_off_order_ids._ids):
            for order in self:
                order.call_off_order_count = len(order.call_off_order_ids)
        else:
            count_by_blanket_order_id = {
                group["blanket_order_id"][0]: group["blanket_order_id_count"]
                for group in self.env["sale.order"].read_group(
                    domain=[("blanket_order_id", "in", self._ids)],
                    fields=["blanket_order_id:count"],
                    groupby=["blanket_order_id"],
                    orderby="blanket_order_id.id",
                )
            }
            for order in self:
                order.call_off_order_count = count_by_blanket_order_id.get(order.id, 0)

    @api.depends("blanket_need_to_be_finalized", "state", "order_type")
    def _compute_is_blanket_reservation_strategy_editable(self):
        for order in self:
            order.is_blanket_reservation_strategy_editable = (
                order.state not in ("cancel", "sent")
                and (order.blanket_need_to_be_finalized or order.state == "draft")
                and order.order_type == "blanket"
            )

    @api.depends("blanket_need_to_be_finalized", "state", "order_type")
    def _compute_is_blanket_eol_strategy_editable(self):
        for order in self:
            order.is_blanket_eol_strategy_editable = (
                order.state not in ("cancel", "sent")
                and (order.blanket_need_to_be_finalized or order.state == "draft")
                and order.order_type == "blanket"
            )

    def _check_blanket_reservation_strategy_editable(self, vals):
        if "blanket_reservation_strategy" in vals:
            for order in self:
                if order.is_blanket_reservation_strategy_editable:
                    continue
                raise ValidationError(
                    _(
                        "The reservation strategy cannot be modified on order %(order)s.",
                        order=order.name,
                    )
                )

    def _check_blanket_eol_strategy_editable(self, vals):
        if "blanket_eol_strategy" in vals:
            for order in self:
                if order.is_blanket_eol_strategy_editable:
                    continue
                raise ValidationError(
                    _(
                        "The end-of-life strategy cannot be modified on order %(order)s.",
                        order=order.name,
                    )
                )

    def action_view_call_off_orders(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("sale.action_orders")
        action["domain"] = [("blanket_order_id", "=", self.id)]
        action["context"] = dict(
            self._context,
            default_blanket_order_id=self.id,
            default_partner_id=self.partner_id.id,
            default_order_type="call_off",
        )
        return action

    def _action_confirm(self):
        # The confirmation process is different for each type of order
        # so we need to split the orders by type before processing them
        # normally.
        blanket_orders = self.browse()
        call_off_orders = self.browse()
        orders = self.browse()
        for order in self:
            if order.order_type == "blanket":
                blanket_orders |= order
            elif order.order_type == "call_off":
                call_off_orders |= order
            else:
                orders |= order
        if blanket_orders:
            blanket_orders._on_blanket_order_confirm()

        orders._split_for_blanket_order()

        if call_off_orders:
            call_off_orders._on_call_off_order_confirm()
        return super(SaleOrder, self.with_context(from_confirm=True))._action_confirm()

    def release_reservation(self):
        # Override to release the stock reservation for the order.
        # The reservation is not released if the order is a blanket order
        # and the method is called from the _action_confirm method.
        to_unreserve = self
        if self.env.context.get("from_confirm"):
            to_unreserve = self.filtered(lambda order: order.order_type != "blanket")
        return super(SaleOrder, to_unreserve).release_reservation()

    def _link_lines_to_blanket_order_line(self):
        """Link the order lines to the blanket order lines."""
        self.order_line._link_to_blanket_order_line()

    def _on_blanket_order_confirm(self):
        """This method is called when a blanket order is confirmed.

        It's responsible to implement the specific behavior of a blanket order.
        By default, it will call the method responsible of the reservation
        strategy implementation and set the commitment date at the start of the
        validity period. It can be overriden to implement additional behavior.
        """
        invalid_orders = self.filtered(lambda order: order.order_type != "blanket")
        if invalid_orders:
            raise ValidationError(
                _("Only blanket orders can be confirmed as blanket orders.")
            )
        # trigger validation on sale order lines for constrains
        # _validate_fields We force the validation to be done here
        # even if it will be done later at flush time. This is to
        # ensure that the data are correct before performing any others
        # operations that could use the data.
        self.order_line._check_blanket_product_not_overlapping()
        for order in self:
            order.commitment_date = order.blanket_validity_start_date
        self.blanket_need_to_be_finalized = True
        self._blanket_order_reserve_call_off_remaining_qty()

    def _on_call_off_order_confirm(self):
        """This method is called when a call-off order is confirmed.

        It's responsible to implement the specific behavior of a call-off order.
        It can be overriden to implement additionalbehavior.
        """
        invalid_orders = self.filtered(lambda order: order.order_type != "call_off")
        if invalid_orders:
            raise ValidationError(
                _("Only call-off orders can be confirmed as call-off orders.")
            )
        self._link_lines_to_blanket_order_line()

    def _ensure_reservation_strategy(self, strategy):
        """Ensure the reservation strategy is the expected one."""
        invalid_orders = self.filtered(
            lambda order: order.blanket_reservation_strategy != strategy
        )
        if invalid_orders:
            ref = ", ".join(invalid_orders.mapped("name"))
            raise ValueError(
                f"Invalid reservation strategy {strategy} for the blanket orders {ref}."
            )

    def _blanket_order_reserve_call_off_remaining_qty(self):
        """Reserve the stock for the blanket order.

        This method should only take care of the potentiel stock reservation
        for the qty available to call off.
        """
        self._ensure_reservation_strategy("at_call_off")

        # By setting the manual delivery flag to True, the delivery will not be
        # created at confirmation time. The delivery process will be triggered by
        # the system when a call-off order is confirmed.
        self._set_manual_delivery(True)

    def _blanket_order_release_call_off_remaining_qty(self):
        """Release the stock reservation for the blanket order.

        This method should only take care of the potentiel stock reservation
        for the qty available to call off.
        """
        self._ensure_reservation_strategy("at_call_off")
        # reset the manual delivery flag to False
        self._set_manual_delivery(False)

    def _set_manual_delivery(self, value):
        """Set manual delivery."""
        # the manual delivery can oly be set on draft orders. Unfortunatly, the
        # state could be set to sale or done at this point.... We will temporarily
        # reset the state to draft to be able to set the manual delivery flag
        for order in self:
            old_state = order.state
            order.state = "draft"
            order.manual_delivery = value
            order.state = old_state

    def _split_for_blanket_order(self):
        """Split the orders for the blanket order.

        This method is called for orders. If some order lines are related
        to a blanket order, it will create a call-off order for each of them and
        remove them from the original order.

        The method returns the call-off orders that have been created or an empty
        recordset if no call-off orders have been created.
        """
        if any(self.filtered(lambda order: order.order_type != "order")):
            raise ValueError("Only orders can be split.")

        splitable_orders = self.filtered(
            lambda order: order.create_call_off_from_so_if_possible
        )
        if not splitable_orders:
            return self.browse()
        blanket_order_candidates = splitable_orders._get_blanket_order_candidates()
        if not blanket_order_candidates:
            return self.browse()
        matchings_dict = self.env["sale.order.line"]._match_lines_to_blanket(
            splitable_orders.order_line, blanket_order_candidates.order_line
        )
        new_call_off_by_order = defaultdict(lambda: self.env["sale.order"])
        # From here, we will create the call-off orders for the matched lines
        # For each line, we will look to the matching blanket lines
        # If the blanket line has enough remaining quantity for the line,
        # We move the line to a new call-off order created for the blanket order
        # Otherwise, we split order line: one line with the quantity of the blanket line
        # and another line with the remaining quantity. The first line is moved to a new
        # call-off order created for the blanket order and the second line is kept in the
        # original order but we will try to match it with another blanket line if one exists.
        # We will repeat this process until all the lines are processed.
        for lines, blanket_lines in matchings_dict.values():
            if not blanket_lines:
                continue
            remaining_qty = sum(blanket_lines.mapped("call_off_remaining_qty"))
            rounding = blanket_lines[0].product_uom.rounding
            if (
                float_compare(
                    remaining_qty,
                    0.0,
                    precision_rounding=blanket_lines[0].product_uom.rounding,
                )
                <= 0
            ):
                continue
            for line in lines:
                for blanket_line in blanket_lines:
                    blanket_order = blanket_line.order_id
                    call_off = new_call_off_by_order[line.order_id]
                    if not call_off:
                        call_off = line.order_id._create_call_off_order(blanket_order)
                        new_call_off_by_order[line.order_id] = call_off
                    qty_deliverable = blanket_line.call_off_remaining_qty
                    original_order = line.order_id
                    if (
                        float_compare(
                            qty_deliverable,
                            line.product_uom_qty,
                            precision_rounding=rounding,
                        )
                        >= 0
                    ):
                        # The blanket line has enough remaining quantity for the line
                        # We move the line to the call-off order
                        line.price_unit = 0
                        line.order_id = call_off
                        self._log_line_moved_to_call_off(line, call_off, original_order)
                        break
                    # The blanket line does not have enough remaining quantity for the line
                    # We split the line and move the part deliverable to the call-off order
                    new_line = line.copy(
                        default={
                            "product_uom_qty": qty_deliverable,
                            "order_id": call_off.id,
                            "price_unit": 0,
                        }
                    )
                    line.product_uom_qty -= qty_deliverable
                    self._log_line_partially_moved_to_call_off(
                        new_line, line, call_off, original_order, qty_deliverable
                    )
        # values() is a generator of sets of values. We want to concatenate all the sets
        # into a single set of values.
        new_call_off_orders = self.env["sale.order"]
        for call_off in new_call_off_by_order.values():
            new_call_off_orders |= call_off
        new_call_off_orders.action_confirm()
        return new_call_off_orders

    def _log_line_moved_to_call_off(self, line, call_off, original_order):
        """Log the line movement to the call-off order."""
        original_order.message_post(
            body=_(
                _(
                    "The line %(line)s has been moved to a new call-off order %(call_off)s."
                ),
                line=line.display_name,
                call_off=call_off._get_html_link(),
            )
        )
        call_off.message_post(
            body=_(
                _("The line %(line)s has been moved from order %(order)s."),
                line=line.display_name,
                order=original_order._get_html_link(),
            )
        )

    def _log_line_partially_moved_to_call_off(
        self, new_line, line, call_off, original_order, qty_deliverable
    ):
        """Log the line partial movement to the call-off order."""
        call_off.message_post(
            body=_(
                _(
                    "The line %(line)s has been created from order %(order)s. "
                    "(Qty moved: %(qty_deliverable)s)"
                ),
                line=new_line.display_name,
                order=original_order._get_html_link(),
                qty_deliverable=qty_deliverable,
            )
        )
        original_order.message_post(
            body=_(
                _(
                    "The line %(line)s has been partially moved to a new call-off "
                    "order %(call_off)s. (Qty moved: %(qty_deliverable)s)"
                ),
                line=line.display_name,
                call_off=call_off._get_html_link(),
                qty_deliverable=qty_deliverable,
            )
        )

    def _get_default_call_off_order_values(self, blanket_order_id):
        """Get the default values to create a new call-off order."""
        self.ensure_one()
        vals = {
            "partner_id": self.partner_id.id,
            "order_type": "call_off",
            "blanket_order_id": blanket_order_id.id,
            "order_line": False,
        }
        if self.commitment_date:
            vals["commitment_date"] = self.commitment_date
        return vals

    def _create_call_off_order(self, blanket_order_id):
        """Get the values to create a new call-off order from the current order."""
        self.ensure_one()
        return self.copy(self._get_default_call_off_order_values(blanket_order_id))

    def _get_single_blanket_order_candidates_domain(self):
        """Get the domain to search for a blanket order candidates."""
        self.ensure_one()
        validity_date = self.commitment_date or self.date_order or fields.Date.today()
        validity_date = fields.Date.to_string(validity_date)
        return [
            ("partner_id", "=", self.partner_id.id),
            ("partner_shipping_id", "=", self.partner_shipping_id.id),
            ("order_type", "=", "blanket"),
            ("state", "in", ("sale", "done")),
            ("blanket_validity_start_date", "<=", validity_date),
            ("blanket_validity_end_date", ">=", validity_date),
        ]

    def _get_blanket_order_candidates_domain(self):
        """Get the domain to search for the blanket order candidates."""
        domains = []
        for order in self:
            order_domain = order._get_single_blanket_order_candidates_domain()
            domains.append(order_domain)
        return expression.OR(domains)

    def _get_blanket_order_candidates(self):
        """Get the blanket order candidates for the order lines."""
        return self.env["sale.order"].search(
            self._get_blanket_order_candidates_domain(), order="id"
        )

    def _cron_manage_blanket_order_eol(self):
        """Manage the end-of-life of the blanket orders."""
        blanket_orders = self.search(
            [
                ("order_type", "=", "blanket"),
                ("state", "in", ("sale", "done")),
                ("blanket_validity_end_date", "<", fields.Date.today()),
                ("blanket_need_to_be_finalized", "=", True),
            ]
        )
        blanket_orders._blanket_order_eol()

    def _blanket_order_eol(self):
        """End-of-life process for the blanket orders."""
        self.filtered(
            lambda order: order.blanket_eol_strategy == "deliver"
        )._blanket_order_deliver_remaining_qty()
        self.write({"blanket_need_to_be_finalized": False})

    def _blanket_order_deliver_remaining_qty(self):
        """Deliver the remaining quantity for the blanket orders.

        We will create a call-off order for the remaining quantity of the blanket order.
        and confirm it.
        """
        for record in self:
            order_lines = []
            for line in record.order_line:
                if (
                    float_compare(
                        line.call_off_remaining_qty,
                        0,
                        precision_rounding=line.product_uom.rounding,
                    )
                    > 0
                ):
                    order_lines.append(
                        Command.create(
                            line._prepare_call_of_vals_to_deliver_blanket_remaining_qty()
                        )
                    )
            if order_lines:
                call_off_order = self.env["sale.order"].create(
                    record._prepare_call_of_vals_to_deliver_blanket_remaining_qty()
                )
                call_off_order.order_line = order_lines
                call_off_order.action_confirm()

    def _prepare_call_of_vals_to_deliver_blanket_remaining_qty(self):
        """Prepare the values to create a call-off order for the remaining quantity."""
        self.ensure_one()
        vals = self._get_default_call_off_order_values(self)
        vals["commitment_date"] = self.blanket_validity_end_date
        return vals

    def _split_recrodset_for_reservation_strategy(self, strategy):
        """Split the orders for the reservation strategy.

        This method will return a tuple where the first element is
        the recordset with the expected reservation strategy and the
        second element is the recordset without the expected reservation
        strategy.
        """
        other_orders = self.browse()
        orders_with_strategy = self.browse()
        for order in self:
            if order.blanket_reservation_strategy == strategy:
                orders_with_strategy |= order
            else:
                other_orders |= order
        return orders_with_strategy, other_orders

    def _before_reservation_strategy_changed(self, old_value, new_value):
        """Method called when the reservation strategy is modified."""
        self.ensure_one()
        self._blanket_order_release_call_off_remaining_qty()

    def _after_reservation_strategy_changed(self, old_value, new_value):
        self.ensure_one()
        if self.state in ("sale", "done"):
            self._blanket_order_reserve_call_off_remaining_qty()

    @contextmanager
    def _notify_reservation_strategy_changed(self, values):
        """Notify the reservation strategy change"""
        strategy_by_record = {}
        new_strategy = values.get("blanket_reservation_strategy")
        if "blanket_reservation_strategy" in values:
            strategy_by_record = {
                record: record.blanket_reservation_strategy
                for record in self
                if record.blanket_reservation_strategy != new_strategy
            }
            for record, old_strategy in strategy_by_record.items():
                record._before_reservation_strategy_changed(old_strategy, new_strategy)
        yield
        if new_strategy:
            for record, old_strategy in strategy_by_record.items():
                record._after_reservation_strategy_changed(old_strategy, new_strategy)

    def write(self, values):
        self._check_blanket_reservation_strategy_editable(values)
        self._check_blanket_eol_strategy_editable(values)
        with self._notify_reservation_strategy_changed(values):
            return super().write(values)

    def _action_cancel(self):
        self.filtered(
            lambda so: so.order_type == "blanket"
            and so.blanket_reservation_strategy == "at_call_off"
        )._blanket_order_release_call_off_remaining_qty()
        return super()._action_cancel()
