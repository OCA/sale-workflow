# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_last_sale(self):
        """ Get last sale price, last sale date and last customer """
        lines = self.env['sale.order.line'].search(
            [('product_id', '=', self.id),
             ('state', 'in', ['sale', 'done'])]).sorted(
            key=lambda l: l.order_id.date_order, reverse=True)
        self.last_sale_date = lines[:1].order_id.date_order
        self.last_sale_price = lines[:1].price_unit
        self.last_customer_id = lines[:1].order_id.partner_id

    last_sale_price = fields.Float(
        string='Last Sale Price', compute='_compute_last_sale')
    last_sale_date = fields.Date(
        string='Last Sale Date', compute='_compute_last_sale')
    last_customer_id = fields.Many2one(
        comodel_name='res.partner', string='Last Customer',
        compute='_compute_last_sale')
