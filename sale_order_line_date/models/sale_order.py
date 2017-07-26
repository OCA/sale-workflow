# -*- coding: utf-8 -*-
# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Eficent Business and IT Consulting Services, S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.onchange('requested_date')
    def onchange_requested_date(self):
        """Warn if the requested dates is sooner than the commitment date"""
        result = super(SaleOrder, self).onchange_requested_date()
        if not result:
            result = {}
        if not self:
            return result
        self.ensure_one()
        if 'warning' not in result:
            lines = []
            for line in self.order_line:
                lines.append((1, line.id, {'requested_date':
                                           self.requested_date}))
            result['value'] = {'order_line': lines}
        return result
