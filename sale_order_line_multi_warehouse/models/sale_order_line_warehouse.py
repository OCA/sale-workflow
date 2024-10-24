# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLineWarehouse(models.Model):
    _name = "sale.order.line.warehouse"
    _description = "Sale Order Line Warehouse"

    order_line_id = fields.Many2one(
        string="Sale Order Line",
        comodel_name="sale.order.line",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        related="order_line_id.product_id",
    )
    product_uom_qty = fields.Float(
        string="Quantity",
        digits="Product Unit of Measure",
    )
    product_uom_id = fields.Many2one(
        string="UoM", comodel_name="uom.uom", related="order_line_id.product_uom"
    )
    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        required=True,
        domain="[('id', 'in', suitable_warehouse_ids)]",
    )
    suitable_warehouse_ids = fields.Many2many(
        comodel_name="stock.warehouse",
        related="order_line_id.order_id.suitable_warehouse_ids",
    )
    move_ids = fields.One2many(
        string="Moves",
        comodel_name="stock.move",
        inverse_name="sale_order_line_warehouse_id",
    )
    qty_delivered = fields.Float(
        string="Qty. Delivered",
        digits="Product Unit of Measure",
        compute="_compute_qty_delivered",
    )
    qty_forecast = fields.Float(
        string="Forecast Qty.",
        compute="_compute_qty_forecast",
        digits="Product Unit of Measure",
    )
    qty_forecast_uom_id = fields.Many2one(
        string="Forecast Qty. UoM", comodel_name="uom.uom", related="product_id.uom_id"
    )

    def name_get(self):
        result = []
        for rec in self:
            name = "{} - {}: {} {}".format(
                rec.warehouse_id.code,
                rec.warehouse_id.name,
                rec.product_uom_qty,
                rec.product_uom_id.name,
            )
            result.append((rec.id, name))
        return result

    @api.depends("product_id", "warehouse_id")
    def _compute_qty_forecast(self):
        for line in self:
            date = (
                line.order_line_id.order_id.commitment_date
                or line.order_line_id._expected_date()
            )
            line.qty_forecast = line.product_id.with_context(
                to_date=date, warehouse=line.warehouse_id.id
            ).virtual_available

    @api.depends(
        "order_line_id.move_ids.state",
        "order_line_id.move_ids.scrapped",
        "order_line_id.move_ids.quantity_done",
        "order_line_id.move_ids.product_uom",
    )
    def _compute_qty_delivered(self):
        for line in self:
            qty = 0.0
            order_line = line.order_line_id
            if order_line.qty_delivered_method == "stock_move":
                (
                    outgoing_moves,
                    incoming_moves,
                ) = order_line._get_outgoing_incoming_moves()
                for move in outgoing_moves.filtered(
                    lambda a: a.warehouse_id == line.warehouse_id
                    or a.picking_id.location_id.warehouse_id == line.warehouse_id
                ):
                    if move.state != "done":
                        continue
                    qty += move.product_uom._compute_quantity(
                        move.quantity_done,
                        order_line.product_uom,
                        rounding_method="HALF-UP",
                    )
                for move in incoming_moves.filtered(
                    lambda a: a.warehouse_id == line.warehouse_id
                    or a.picking_id.location_id.warehouse_id == line.warehouse_id
                ):
                    if move.state != "done":
                        continue
                    qty -= move.product_uom._compute_quantity(
                        move.quantity_done,
                        order_line.product_uom,
                        rounding_method="HALF-UP",
                    )
            line.qty_delivered = qty

    def write(self, values):
        ret_vals = super().write(values)
        if "product_uom_qty" in values:
            for order_line in self.mapped("order_line_id"):
                order_line.with_context(bypass_write_order_line_warehouse=True).write(
                    {
                        "product_uom_qty": sum(
                            order_line.mapped("sale_order_line_warehouse_ids").mapped(
                                "product_uom_qty"
                            )
                        )
                    }
                )
        return ret_vals

    def create(self, vals_list):
        lines = super().create(vals_list)
        for order_line in lines.mapped("order_line_id"):
            # Do not adjust warehouse distribution lines quantity as it has already
            # been set here
            order_line.with_context(bypass_write_order_line_warehouse=True).write(
                {
                    "product_uom_qty": sum(
                        order_line.mapped("sale_order_line_warehouse_ids").mapped(
                            "product_uom_qty"
                        )
                    )
                }
            )
        return lines

    def unlink(self):
        if not self.env.context.get("bypass_write_order_line_warehouse", False):
            # Do not adjust warehouse distribution lines quantity as it has already
            # been set here
            self.with_context(bypass_write_order_line_warehouse=True).write(
                {"product_uom_qty": 0.0}
            )
        return super().unlink()
