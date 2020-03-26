# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    timely_delivery = fields.Boolean(
        string='Timely delivery', copy=False, readonly=True,
        help=u'True if the 1st delivery meets the announced deadline')
