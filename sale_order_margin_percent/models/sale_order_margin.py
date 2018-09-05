##############################################################################
#
#    OmniaSolutions, Open Source Management Solution
#    2010-2018 OmniaSolutions (<http://www.omniasolutions.eu>).
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
##############################################################################

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    percent = fields.Float(
        string='Percent',
        compute='_compute_percent')

    @api.depends('margin', 'amount_untaxed')
    def _compute_percent(self):
        for order in self:
            if order.margin and order.amount_untaxed:
                order.percent = (order.margin / order.amount_untaxed) * 100
