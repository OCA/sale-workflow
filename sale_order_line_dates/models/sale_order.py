# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def onchange_requested_date(self, requested_date, commitment_date):
        """Warn if the requested dates is sooner than the commitment date"""
        result = super(SaleOrder, self).onchange_requested_date(
            requested_date, commitment_date)
        if not self:
            return result
        self.ensure_one()
        if 'warning' not in result:
            lines = []
            for line in self.order_line:
                lines.append((1, line.id, {'requested_date': requested_date}))
            result['value'] = {'order_line': lines}
        return result

    @api.model
    def _get_date_planned(self, order, line, start_date):
        if line.requested_date:
            return line.requested_date
        else:
            return super(SaleOrder, self)._get_date_planned(
                order, line, start_date)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    requested_date = fields.Datetime(string='Requested Date')
