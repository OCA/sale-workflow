# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models


class SaleOrderConfirmPartialLine(models.TransientModel):
    _name = "sale.order.confirm.partial.line"
    _description = "Partial Quotation Confirmation Line"

    wizard_id = fields.Many2one(
        comodel_name="sale.order.confirm.partial",
        required=True,
    )
    so_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Order Line",
        domain="[('order_id', '=', parent.sale_order_id)]",
        required=True,
    )
    confirmed_qty = fields.Float(
        string="Confirmed Quantity",
        compute="_compute_confirmed_qty",
        readonly=False,
        required=True,
        store=True,
    )

    @api.constrains("confirmed_qty", "so_line_id")
    def _check_confirmed_qty(self):
        for line in self:
            if line.confirmed_qty < 0:
                raise exceptions.ValidationError(
                    _("Confirmed quantity cannot be negative.")
                )
            if line.confirmed_qty > line.so_line_id.product_uom_qty:
                raise exceptions.ValidationError(
                    _("Confirmed quantity cannot be greater than ordered quantity.")
                )

    @api.depends("so_line_id")
    def _compute_confirmed_qty(self):
        for line in self:
            line.confirmed_qty = line.so_line_id.product_uom_qty
