# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class sale_order_line_pack_line(models.Model):
    _name = 'sale.order.line.pack.line'
    _description = 'sale.order.line.pack.line'

    order_line_id = fields.Many2one(
        'sale.order.line',
        'Order Line',
        ondelete='cascade',
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
    price_subtotal = fields.Float(
        compute="_amount_line",
        string='Subtotal',
        digits=dp.get_precision('Account')
        )
    product_uom_qty = fields.Float(
        'Quantity',
        digits=dp.get_precision('Product UoS'),
        required=True)

    @api.one
    @api.onchange('product_id')
    def onchange_product_id(self):
        self.price_unit = self.product_id.lst_price

    @api.one
    @api.depends('price_unit', 'product_uom_qty')
    def _amount_line(self):
        self.price_subtotal = self.product_uom_qty * self.price_unit
