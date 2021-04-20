# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ManualDeliveryLine(models.TransientModel):
    _name = "manual.delivery.line"
    _description = "Manual Delivery Line"

    manual_delivery_id = fields.Many2one(
        "manual.delivery", string="Wizard manual procurement"
    )
    order_line_id = fields.Many2one("sale.order.line", string="Sale Order Line",)
    product_id = fields.Many2one(
        "product.product", string="Product", related="order_line_id.product_id",
    )
    line_description = fields.Text(string="Description", related="order_line_id.name",)
    ordered_qty = fields.Float(
        "Ordered quantity",
        related="order_line_id.product_uom_qty",
        help="Quantity ordered in the related Sale Order",
    )
    existing_qty = fields.Float(
        "Existing quantity",
        help="Quantity already planned or shipped (stock movements \
            already created)",
    )
    remaining_qty = fields.Float(
        "Remaining quantity",
        compute="_compute_remaining_qty",
        help="Remaining quantity available to deliver",
    )
    to_ship_qty = fields.Float("Quantity to Ship")

    @api.multi
    @api.depends("to_ship_qty")
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.ordered_qty - line.existing_qty - line.to_ship_qty
