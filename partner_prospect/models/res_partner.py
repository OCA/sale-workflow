# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends('commercial_partner_id',
                 'commercial_partner_id.sale_order_ids',
                 'commercial_partner_id.sale_order_ids.state',
                 'commercial_partner_id.child_ids',
                 'commercial_partner_id.child_ids.sale_order_ids',
                 'commercial_partner_id.child_ids.sale_order_ids.state')
    def _compute_prospect(self):
        sale_ids = (
            self.commercial_partner_id.sale_order_ids +
            self.commercial_partner_id.mapped('child_ids.sale_order_ids'))
        self.prospect = not sale_ids.filtered(
            lambda r: r.state not in ('draft', 'sent', 'cancel'))

    prospect = fields.Boolean(
        string='Prospect', compute='_compute_prospect', store=True)
