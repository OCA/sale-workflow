# -*- coding: utf-8 -*-
# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    requested_date = fields.Datetime()

    @api.multi
    def write(self, vals):
        for line in self:
            if not line.requested_date and line.order_id.requested_date:
                vals.update({'requested_date': line.order_id.requested_date})
        return super(SaleOrderLine, self).write(vals)

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        if res.order_id.requested_date and not res.requested_date:
            res.write({'requested_date': res.order_id.requested_date})
        return res

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        vals = super(SaleOrderLine, self).\
            _prepare_order_line_procurement(group_id)
        if self.requested_date:
            vals.update({'date_planned': self.requested_date})
        return vals
