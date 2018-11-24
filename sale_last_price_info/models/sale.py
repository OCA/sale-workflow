# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    date_order_sale_last_price_info = fields.Datetime(
        string='Order date', related='order_id.date_order',
        store=True, index=True)
