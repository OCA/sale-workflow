# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.one
    def _get_last_sale(self):
        """ Get last sale price, last sale date and last customer """
        lines = self.env['sale.order.line'].search(
            [('product_id', '=', self.id),
             ('state', 'in', ['confirmed', 'done'])]).sorted(
            key=lambda l: l.order_id.date_order, reverse=True)
        self.last_sale_date = lines[:1].order_id.date_order
        self.last_sale_price = lines[:1].price_unit
        self.last_customer_id = lines[:1].order_id.partner_id

    last_sale_price = fields.Float(
        string='Last Sale Price', compute='_get_last_sale')
    last_sale_date = fields.Date(
        string='Last Sale Date', compute='_get_last_sale')
    last_customer_id = fields.Many2one(
        comodel_name='res.partner', string='Last Customer',
        compute='_get_last_sale')
