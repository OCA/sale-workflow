# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
        strting="Suitable Warehouses",
        comodel_name="stock.warehouse",
        related="order_id.suitable_warehouse_ids",
    )

    @api.constrains("sale_order_line_warehouse_ids")
    def _check_warehouses(self):
        for line in self:
            warehouse_lines_group = self.env["sale.order.line.warehouse"].read_group(
                domain=[("order_line_id", "=", line.id)],
                fields=["warehouse_id"],
                groupby=["warehouse_id"],
            )
            if warehouse_lines_group and any(
                a.get("warehouse_id_count") > 1 for a in warehouse_lines_group
            ):
                raise ValidationError(_("Only one warehouse per line allowed"))

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
            lambda a: not a.move_ids and a.product_uom_qty == 0.0
        ).unlink()
        return ret_vals

    def create(self, vals_list):
        lines = super().create(vals_list)
        # Automatically create a warehouse distributions line when the
        # sale order allows multi warehouse.
        for line in lines.filtered("allow_sale_multi_warehouse"):
            if line.move_ids:
                # This part is executed when a sale order line is created by adding
                # a stock move in a picking related to the sale order.
                self.env["sale.order.line.warehouse"].create(
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
                self.env["sale.order.line.warehouse"].create(
                    {
                        "order_line_id": line.id,
                        "product_uom_qty": line.product_uom_qty,
                        "warehouse_id": line.order_id.warehouse_id.id,
                    }
                )
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
                lambda a: a.product_uom_qty > 0.0
            )
        )
        pending_qty = qty
        while pending_qty > 0.0:
            if reduce_line:
                if reduce_line[0].product_uom_qty >= pending_qty:
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
                    lambda a: a.product_uom_qty > 0.0
                )
            else:
                raise ValidationError(_("Amount cannot be reduced."))

    def adjust_qty_assigned_to_warehouse_increase(self, qty):
        self.ensure_one()
        default_warehouse_lines = self._get_adjustment_default_warehouse_line()
        pending_qty = -1 * qty
        # This part is executed when a sale order line is added by adding a
        # stock move in a picking related to the order
        if self.qty_delivered > self.product_uom_qty:
            delivered_line = self.sale_order_line_warehouse_ids.filtered(
                lambda a: a.qty_delivered > a.product_uom_qty
            )
            while delivered_line and pending_qty > 0.0:
                qty_to_add = min(
                    delivered_line[0].qty_delivered - delivered_line[0].product_uom_qty,
                    pending_qty,
                )
                delivered_line[0].write({"product_uom_qty": qty_to_add})
                pending_qty -= qty_to_add
                delivered_line = self.sale_order_line_warehouse_ids.filtered(
                    lambda a: a.qty_delivered > a.product_uom_qty
                )
        if pending_qty > 0.0:
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
            if qty > 0.0:
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

        if self.product_id.tracking == "serial" and self.state == "assigned":
            self.next_serial = self.env["stock.lot"]._get_next_serial(
                self.company_id, self.product_id
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
