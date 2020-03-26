# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models
import pytz


def _tz_get(self):
    return [(tz, tz) for tz in sorted(
        pytz.all_timezones, key=lambda tz: tz if not tz.startswith(
            'Etc/') else '_')]


class resCompany(models.Model):
    _inherit = 'res.company'

    order_limit_hour = fields.Float(
        string='Order limit hour (HH:00)',
        help=u'Prepared the same day if ordered before the hour entered')
    tz = fields.Selection(
        _tz_get, string='Timezone',
        help=u'Timezone used for the confirmation date in the sale order')
