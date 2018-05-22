##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class SaleOrderLinePackLine(models.Model):
    _name = 'sale.order.line.pack.line'
    _description = 'Sale Order None Detailed Pack Lines'

    order_line_id = fields.Many2one(
        'sale.order.line',
        'Order Line',
        ondelete='cascade',
        index=True,
        required=True
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        required=True
    )
    price_unit = fields.Float(
        'Unit Price',
        required=True,
        digits=dp.get_precision('Product Price')
    )
    discount = fields.Float(
        'Discount (%)',
        digits=dp.get_precision('Discount'),
    )
    price_subtotal = fields.Float(
        compute="_compute_price_subtotal",
        string='Subtotal',
        digits=dp.get_precision('Account')
    )
    product_uom_qty = fields.Float(
        'Quantity',
        digits=dp.get_precision('Product UoS'),
        required=True
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        for line in self:
            line.price_unit = line.product_id.lst_price

    @api.depends('price_unit', 'product_uom_qty')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = (
                line.product_uom_qty * line.price_unit *
                (1 - (line.discount or 0.0) / 100.0))
