# -*- coding: utf-8 -*-
# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

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
