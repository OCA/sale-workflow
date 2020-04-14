# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, api
import pytz


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    on_time_delivery = fields.Boolean(
        string='On time delivery', compute='_compute_on_time_delivery',
        store=True, copy=False, readonly=True,
        help=u'True if the 1st delivery meets the announced deadline')
    check_preparation_time = fields.Boolean(
        string='Check preparation time',
        related='company_id.check_preparation_time', readonly=True)

    @api.depends('effective_date')
    def _compute_on_time_delivery(self):
        for order in filter(lambda x: x.check_preparation_time and
                            x.effective_date, self):
            local_tz = pytz.timezone(order.company_id.tz)
            confirmation_date_tz = local_tz.localize(
                order.confirmation_date)
            order_hour = confirmation_date_tz.hour
            order_limit_hour = int(order.company_id.order_limit_hour)
            confirmation_date = fields.Date.from_string(
                confirmation_date_tz)
            effective_date = fields.Date.from_string(order.effective_date)
            delta = effective_date - confirmation_date
            if order_hour < order_limit_hour and delta.days <= 1:
                order.on_time_delivery = True
