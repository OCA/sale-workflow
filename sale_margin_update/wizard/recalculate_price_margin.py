# Copyright 2024 SDi Sidoo Soluciones S.L. <www.sidoo.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleRecalculatePriceMargin(models.TransientModel):
    _name = "sale.recalculate.price.margin"
    _description = "Recalculate Price By Margin"

    sale_margin_percent = fields.Float(
        string="Margin (%)",
        digits="Product Price",
        required=True,
    )
    line_id = fields.Many2one("sale.order.line", ondelete="cascade")
    order_id = fields.Many2one("sale.order", ondelete="cascade")

    @api.onchange("sale_margin_percent")
    def _onchange_sale_margin_percent(self):
        if self.sale_margin_percent < 0:
            raise UserError(_("Margin can't be negative"))
        if self.sale_margin_percent >= 100:
            raise UserError(_("Margin can't be greater than 100"))

    def recalculate_price_margin(self):
        self.ensure_one()
        lines = self.order_id.order_line
        if self.line_id:
            lines = self.line_id
        for line in lines.filtered(lambda x: x.product_id):
            if self.sale_margin_percent == 100:
                price_subtotal = (line.purchase_price * line.product_uom_qty) * 2
            elif self.sale_margin_percent == 0:
                price_subtotal = line.purchase_price * line.product_uom_qty
            else:
                price_subtotal = (line.purchase_price * line.product_uom_qty) / (
                    1 - self.sale_margin_percent / 100
                )
            price_unit_with_discount = price_subtotal / line.product_uom_qty
            line.price_unit = price_unit_with_discount / (1 - (line.discount / 100))
