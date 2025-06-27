# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_order_line_warehouse_ids = fields.One2many(
        string="SO Line Warehouses",
        comodel_name="sale.order.line.warehouse",
        inverse_name="order_line_id",
    )
    qty_assigned_to_warehouse = fields.Float(
        string="Qty. Assigned to Warehouses",
        digits="Product Unit of Measure",
        compute="_compute_qty_assigned_to_warehouse",
        store=True,
    )
    allow_sale_multi_warehouse = fields.Boolean(
        related="order_id.allow_sale_multi_warehouse"
    )
    suitable_warehouse_ids = fields.Many2many(
        string="Suitable Warehouses",
        comodel_name="stock.warehouse",
        related="order_id.suitable_warehouse_ids",
    )
    qty_by_warehouse = fields.Binary(
        compute="_compute_qty_by_warehouse", exportable=False
    )
    display_qty_by_warehouse_widget = fields.Boolean(
        compute="_compute_display_qty_by_warehouse_widget"
    )

    @api.constrains("sale_order_line_warehouse_ids")
    def _check_warehouses(self):
        warehouse_lines_group = self.env["sale.order.line.warehouse"].read_group(
            domain=[("order_line_id", "in", self.ids)],
            fields=["warehouse_id"],
            groupby=["warehouse_id", "order_line_id"],
        )
        if warehouse_lines_group and any(
            a.get("warehouse_id_count") > 1 for a in warehouse_lines_group
        ):
            raise ValidationError(_("Only one warehouse per line allowed"))

    def _compute_qty_to_deliver(self):
        ret_vals = super()._compute_qty_to_deliver()
        for line in self.filtered("allow_sale_multi_warehouse"):
            line.display_qty_widget = False
        return ret_vals

    @api.depends(
        "product_type",
        "qty_delivered",
        "state",
        "move_ids",
        "product_uom",
        "allow_sale_multi_warehouse",
    )
    def _compute_display_qty_by_warehouse_widget(self):
        for line in self:
            display_qty_by_warehouse_widget = False
            if (
                line.allow_sale_multi_warehouse
                and line.product_type == "product"
                and line.product_uom
                and line.qty_to_deliver > 0
                and (
                    line.state in ["draft", "sent"]
                    or (line.state == "sale" and line.move_ids)
                )
            ):
                display_qty_by_warehouse_widget = True
            line.display_qty_by_warehouse_widget = display_qty_by_warehouse_widget

    @api.depends(
        "product_id",
        "product_uom_qty",
        "product_uom",
        "order_id.commitment_date",
        "move_ids",
        "move_ids.forecast_expected_date",
        "move_ids.forecast_availability",
        "sale_order_line_warehouse_ids",
    )
    def _compute_qty_by_warehouse(self):
        for line in self:
            qty_by_warehouse = {}
            warehouses = []
            for warehouse in line.suitable_warehouse_ids:
                warehouses.append(line._get_qty_by_warehouse_vals(warehouse))
            qty_by_warehouse["warehouses"] = warehouses
            forecasted_issue = any(
                warehouse.get("forecasted_issue") for warehouse in warehouses
            )
            qty_by_warehouse["forecasted_issue"] = forecasted_issue
            line.qty_by_warehouse = qty_by_warehouse

    # Based on _compute_qty_at_date method in sale.order.line
    def _get_qty_by_warehouse_vals(self, warehouse):
        self.ensure_one()
        scheduled_date = self.order_id.commitment_date or self._expected_date()
        moves = self.move_ids | self.env["stock.move"].browse(
            self.move_ids._rollup_move_origs()
        )
        moves = moves.filtered(
            lambda m: m.product_id == self.product_id
            and m.state not in ("cancel", "done")
            and m.warehouse_id == warehouse
        )

        # qty_available_today
        qty_available_today = 0
        for move in moves:
            qty_available_today += move.product_uom._compute_quantity(
                move.reserved_availability, self.product_uom
            )

        # forecast_expected_date
        forecast_expected_date = False
        if moves:
            forecast_expected_date = max(moves.mapped("forecast_expected_date"))

        # free_qty_today
        free_qty_today = 0.0
        if self.state == "sale":
            for move in moves:
                free_qty_today += move.product_id.uom_id._compute_quantity(
                    move.forecast_availability, self.product_uom
                )
        elif self.state in ["draft", "sent"]:
            free_qty_today = self.product_id.with_context(
                to_date=scheduled_date, warehouse=warehouse.id
            ).free_qty

        # virtual_available_at_date
        virtual_available_at_date = self.product_id.with_context(
            to_date=scheduled_date, warehouse=warehouse.id
        ).virtual_available

        # qty_to_deliver
        to_deliver_from_warehouse = (
            sum(
                self.sale_order_line_warehouse_ids.filtered(
                    lambda a: a.warehouse_id == warehouse
                ).mapped("product_uom_qty")
            )
            or 0.0
        )
        # taken from _compute_qty_delivered in sale.order.line in module
        # sale_stock
        qty_delivered = 0.0
        qty_to_deliver = 0.0
        if self.qty_delivered_method == "stock_move":
            outgoing_moves, incoming_moves = self._get_outgoing_incoming_moves()
            for move in outgoing_moves.filtered(lambda a: a.warehouse_id == warehouse):
                if move.state != "done":
                    continue
                qty_delivered += move.product_uom._compute_quantity(
                    move.quantity_done,
                    self.product_uom,
                    rounding_method="HALF-UP",
                )
            for move in incoming_moves.filtered(lambda a: a.warehouse_id == warehouse):
                if move.state != "done":
                    continue
                qty_delivered -= move.product_uom._compute_quantity(
                    move.quantity_done,
                    self.product_uom,
                    rounding_method="HALF-UP",
                )
            qty_to_deliver = to_deliver_from_warehouse - qty_delivered

        # will_be_fulfilled
        if self.state in ["sale", "done"]:
            will_be_fulfilled = free_qty_today >= qty_to_deliver
        else:
            will_be_fulfilled = virtual_available_at_date >= qty_to_deliver

        # forecasted_issue
        forecasted_issue = False
        if (
            self.state in ["draft", "sent"]
            and not will_be_fulfilled
            and not self.is_mto
        ):
            forecasted_issue = True
        elif not will_be_fulfilled or (
            forecast_expected_date and forecast_expected_date > scheduled_date
        ):
            forecasted_issue = True

        # format forecast_expected_date formatted
        forecast_expected_date_str = ""
        lang = self.env.context.get("lang") or "en_US"
        date_format = self.env["res.lang"]._lang_get(lang).date_format
        if forecast_expected_date:
            forecast_expected_date_str = forecast_expected_date.strftime(date_format)

        return {
            "warehouse": warehouse.id,
            "warehouse_name": warehouse.name,
            "qty_available_today": qty_available_today,
            "virtual_available_at_date": virtual_available_at_date,
            "free_qty_today": free_qty_today,
            "qty_to_deliver": qty_to_deliver,
            "will_be_fulfilled": will_be_fulfilled,
            "forecast_expected_date": forecast_expected_date,
            "scheduled_date": scheduled_date,
            "forecast_expected_date_str": forecast_expected_date_str,
            "forecasted_issue": forecasted_issue,
        }

    def write(self, values):
        # Do not assign quantity to warehouse distribution lines
        # if this write is triggered by write method in
        # sale.order.line.warehouse model.
        if "product_uom_qty" in values and not self.env.context.get(
            "bypass_write_order_line_warehouse", False
        ):
            for line in self.filtered("allow_sale_multi_warehouse"):
                qty = line.product_uom_qty - values.get("product_uom_qty")
                line.adjust_qty_assigned_to_warehouse(qty)
        ret_vals = super().write(values)
        # Delete warehouse distribution lines which are not related to a
        # stock move and their quantity is 0
        self.mapped("sale_order_line_warehouse_ids").filtered(
            lambda a: not a.move_ids
            and float_compare(
                a.product_uom_qty, 0.0, precision_rounding=a.product_uom_id.rounding
            )
            == 0
        ).unlink()
        return ret_vals

    def create(self, vals_list):
        lines = super().create(vals_list)
        # Automatically create a warehouse distributions line when the
        # sale order allows multi warehouse.
        sale_order_line_warehouse_vals = []
        for line in lines.filtered("allow_sale_multi_warehouse"):
            if line.move_ids:
                # This part is executed when a sale order line is created by adding
                # a stock move in a picking related to the sale order.
                sale_order_line_warehouse_vals.append(
                    {
                        "order_line_id": line.id,
                        "product_uom_qty": line.product_uom_qty,
                        "warehouse_id": line.move_ids[
                            0
                        ].picking_id.location_id.warehouse_id.id,
                        "move_ids": [line.move_ids[0].id],
                    }
                )
            else:
                sale_order_line_warehouse_vals.append(
                    {
                        "order_line_id": line.id,
                        "product_uom_qty": line.product_uom_qty,
                        "warehouse_id": line.order_id.warehouse_id.id,
                    }
                )
        if sale_order_line_warehouse_vals:
            self.env["sale.order.line.warehouse"].create(sale_order_line_warehouse_vals)
        return lines

    @api.depends(
        "sale_order_line_warehouse_ids", "sale_order_line_warehouse_ids.product_uom_qty"
    )
    def _compute_qty_assigned_to_warehouse(self):
        for line in self:
            qty = 0.0
            if line.allow_sale_multi_warehouse and line.sale_order_line_warehouse_ids:
                qty = sum(line.sale_order_line_warehouse_ids.mapped("product_uom_qty"))
            line.qty_assigned_to_warehouse = qty

    # Overide this method in case the default warehouse distribution line
    # in which the increase/decrease operations in sale order lines should
    # be applied has to be selected using different conditions.
    def _get_adjustment_default_warehouse_line(self):
        self.ensure_one()
        return self.sale_order_line_warehouse_ids.filtered(
            lambda a: a.warehouse_id == self.order_id.warehouse_id
        )

    def adjust_qty_assigned_to_warehouse_decrease(self, qty):
        self.ensure_one()
        reduce_line = (
            self._get_adjustment_default_warehouse_line()
            or self.sale_order_line_warehouse_ids.filtered(
                lambda a: float_compare(
                    a.product_uom_qty, 0.0, precision_rounding=a.product_uom_id.rounding
                )
                > 0
            )
        )
        pending_qty = qty
        while (
            float_compare(
                pending_qty, 0.0, precision_rounding=self.product_uom.rounding
            )
            > 0
        ):
            if reduce_line:
                if (
                    float_compare(
                        pending_qty,
                        reduce_line[0].product_uom_qty,
                        precision_rounding=self.product_uom.rounding,
                    )
                    < 0
                ):
                    reduce_line[0].write(
                        {
                            "product_uom_qty": reduce_line[0].product_uom_qty
                            - pending_qty
                        }
                    )
                    pending_qty = 0.0
                else:
                    pending_qty -= reduce_line[0].product_uom_qty
                    reduce_line[0].write({"product_uom_qty": 0.0})
                reduce_line = self.sale_order_line_warehouse_ids.filtered(
                    lambda a: float_compare(
                        a.product_uom_qty,
                        0.0,
                        precision_rounding=a.product_uom_id.rounding,
                    )
                    > 0
                )
            else:
                raise ValidationError(
                    _(
                        "Amount for sale order line with product %(product)s could not be "
                        "reduced when automatically adjusting quantitiy as no warehouse "
                        "line could be selected.",
                        product=self.product_id.name,
                    )
                )

    def adjust_qty_assigned_to_warehouse_increase(self, qty):
        self.ensure_one()
        default_warehouse_lines = self._get_adjustment_default_warehouse_line()
        pending_qty = -1 * qty
        # This part is executed when a sale order line is added by adding a
        # stock move in a picking related to the order
        if (
            float_compare(
                self.qty_delivered,
                self.product_uom_qty,
                precision_rounding=self.product_uom.rounding,
            )
            > 0
        ):
            delivered_line = self.sale_order_line_warehouse_ids.filtered(
                lambda a: float_compare(
                    a.qty_delivered,
                    a.product_uom_qty,
                    precision_rounding=a.product_uom_id.rounding,
                )
                > 0
            )
            while (
                float_compare(
                    delivered_line,
                    pending_qty,
                    precision_rounding=self.product_uom.rounding,
                )
                > 0
            ):
                qty_to_add = min(
                    delivered_line[0].qty_delivered - delivered_line[0].product_uom_qty,
                    pending_qty,
                )
                delivered_line[0].write({"product_uom_qty": qty_to_add})
                pending_qty -= qty_to_add
                delivered_line = self.sale_order_line_warehouse_ids.filtered(
                    lambda a: float_compare(
                        a.qty_delivered,
                        a.product_uom_qty,
                        precision_rounding=a.product_uom_id.rounding,
                    )
                    > 0
                )
        if (
            float_compare(
                pending_qty,
                0.0,
                precision_rounding=self.product_uom.rounding,
            )
            > 0
        ):
            if default_warehouse_lines:
                default_warehouse_lines.write(
                    {
                        "product_uom_qty": default_warehouse_lines.product_uom_qty
                        + pending_qty
                    }
                )
            else:
                self.env["sale.order.line.warehouse"].create(
                    {
                        "order_line_id": self.id,
                        "product_uom_qty": pending_qty,
                        "warehouse_id": self.order_id.warehouse_id.id,
                    }
                )

    def adjust_qty_assigned_to_warehouse(self, qty):
        self.ensure_one()
        if self.allow_sale_multi_warehouse:
            # New quantity is lower than previous quantity
            if (
                float_compare(qty, 0.0, precision_rounding=self.product_uom.rounding)
                > 0
            ):
                self.adjust_qty_assigned_to_warehouse_decrease(qty)
            # New quantity is greater than previous quantity
            else:
                self.adjust_qty_assigned_to_warehouse_increase(qty)

    def _get_qty_procurement(self, previous_product_uom_qty=False):
        self.ensure_one()
        qty = super()._get_qty_procurement(previous_product_uom_qty)
        if self.allow_sale_multi_warehouse and self.env.context.get(
            "warehouse_line", False
        ):
            warehouse_line = self.env.context.get("warehouse_line")
            qty_warehouse_line = 0.0
            outgoing_moves, incoming_moves = self._get_outgoing_incoming_moves()
            outgoing_moves = outgoing_moves.filtered(
                lambda a: a.sale_order_line_warehouse_id == warehouse_line
            )
            incoming_moves = incoming_moves.filtered(
                lambda a: a.sale_order_line_warehouse_id == warehouse_line
            )
            for move in outgoing_moves:
                qty_warehouse_line += move.product_uom._compute_quantity(
                    move.product_uom_qty, self.product_uom, rounding_method="HALF-UP"
                )
            for move in incoming_moves:
                qty_warehouse_line -= move.product_uom._compute_quantity(
                    move.product_uom_qty, self.product_uom, rounding_method="HALF-UP"
                )
            qty = (
                self.product_uom_qty
                - warehouse_line.product_uom_qty
                + qty_warehouse_line
            )
        return qty

    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        if self.allow_sale_multi_warehouse and self.env.context.get(
            "warehouse_line", False
        ):
            values.update(
                {
                    "warehouse_id": self.env.context.get("warehouse_line").warehouse_id,
                    "sale_order_line_warehouse_id": self.env.context.get(
                        "warehouse_line"
                    ).id,
                }
            )
        return values

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        ret_vals = True
        for line in self:
            if not (
                line.sale_order_line_warehouse_ids and line.allow_sale_multi_warehouse
            ):
                ret_vals = super(
                    SaleOrderLine, line.with_context(warehouse_line=False)
                )._action_launch_stock_rule(previous_product_uom_qty)
            else:
                for warehouse_line in line.sale_order_line_warehouse_ids:
                    ret_vals = super(
                        SaleOrderLine, line.with_context(warehouse_line=warehouse_line)
                    )._action_launch_stock_rule(previous_product_uom_qty)
        return ret_vals

    def action_show_warehouse_lines(self):
        self.ensure_one()
        view = self.env.ref(
            "sale_order_line_multi_warehouse.sale_order_line_warehouse_view"
        )
        return {
            "name": _("Warehouse Distribution"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "sale.order.line",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
        }
