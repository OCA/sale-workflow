# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, api, fields
import pytz
import ast


def _tz_get(self):
    return [(tz, tz) for tz in sorted(
        pytz.all_timezones, key=lambda tz: tz if not tz.startswith(
            'Etc/') else '_')]


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    order_limit_hour = fields.Float(
        string='Order limit hour (HH:00)',
        help=u'Prepared the same day if ordered before the hour entered')
    tz = fields.Selection(
        _tz_get, string='Timezone',
        help=u'Timezone used for the confirmation date in the sale order')
    check_preparation_time = fields.Boolean(
        string='Check preparation time',
        help=u'True if you want check the preparation time '
             u'of the customer order')

    @api.onchange('check_preparation_time')
    def _onchange_check_preparation_time(self):
        if self.check_preparation_time and not self.tz:
            self.tz = self.env.context.get('tz' or '')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update({
            'check_preparation_time': ast.literal_eval(
                str(self.env['ir.config_parameter'].sudo().get_param(
                    'sale_commitment_lead_time.check_preparation_time'))),
            'order_limit_hour': float(
                self.env['ir.config_parameter'].sudo().get_param(
                    'sale_commitment_lead_time.order_limit_hour')),
            'tz': self.env['ir.config_parameter'].sudo().get_param(
                'sale_commitment_lead_time.tz')})
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        if not self.group_sale_order_dates and self.check_preparation_time:
            self.check_preparation_time = False
        self.env['ir.config_parameter'].sudo().set_param(
            'sale_commitment_lead_time.check_preparation_time',
            self.check_preparation_time)
        self.env['ir.config_parameter'].sudo().set_param(
            'sale_commitment_lead_time.order_limit_hour',
            self.order_limit_hour)
        self.env['ir.config_parameter'].sudo().set_param(
            'sale_commitment_lead_time.tz',
            self.tz)
        if self.company_id.check_preparation_time != self.check_preparation_time:
            self.company_id.check_preparation_time = self.check_preparation_time
        if self.company_id.order_limit_hour != self.order_limit_hour:
            self.company_id.order_limit_hour = self.order_limit_hour
        if self.company_id.tz != self.tz:
            self.company_id.tz = self.tz
