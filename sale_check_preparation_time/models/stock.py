# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import pytz


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        for picking in filter(lambda x: x.picking_type_id.code == 'outgoing' and
                              x.sale_id, self):
            if picking.company_id.tz:
                local_tz = pytz.timezone(picking.company_id.tz)
            else:
                local_tz = pytz.timezone('UTC')
            confirmation_date = local_tz.localize(
                picking.sale_id.confirmation_date)
            order_hour = confirmation_date.hour
            order_limit_hour = int(picking.company_id.order_limit_hour)
            order_date = fields.Date.from_string(
                picking.sale_id.confirmation_date)
            picking_date = fields.Date.from_string(picking.date_done)
            delta = picking_date - order_date
            if order_hour < order_limit_hour and delta.days <= 1:
                picking.sale_id.write({'timely_delivery': True})
        return res
