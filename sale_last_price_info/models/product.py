# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_last_sale(self):
        """ Get last sale price, last sale date and last customer """
        so_line_obj = self.env['sale.order.line']
        for product in self:
            line = so_line_obj.search(
                [('product_id', '=', product.id),
                 ('state', 'in', ['sale', 'done'])], limit=1,
                order="date_order_sale_last_price_info desc")
            product.last_sale_date = \
                fields.Datetime.to_string(
                    line.date_order_sale_last_price_info)
            product.last_sale_price = line.price_unit
            product.last_customer_id = line.order_id.partner_id

    last_sale_price = fields.Float(
        string='Last Sale Price', compute='_compute_last_sale')
    last_sale_date = fields.Date(
        string='Last Sale Date', compute='_compute_last_sale')
    last_customer_id = fields.Many2one(
        comodel_name='res.partner', string='Last Customer',
        compute='_compute_last_sale')
