# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Eficent Business and IT Consulting Services, S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.onchange('commitment_date')
    def _onchange_commitment_date(self):
        """Update order lines with commitment date from sale order"""
        result = super(SaleOrder, self)._onchange_commitment_date() or {}
        if not self:
            return result
        if 'warning' not in result:
            result['value'] = {'order_line': [
                (1, line.id, {'commitment_date': self.commitment_date})
                for line in self.order_line
            ]}
        return result
