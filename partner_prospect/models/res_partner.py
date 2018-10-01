# -*- coding: utf-8 -*-
# (c) 2015 Esther Martin - AvanzOSC
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('commercial_partner_id',
                 'commercial_partner_id.sale_order_ids',
                 'commercial_partner_id.sale_order_ids.state',
                 'commercial_partner_id.child_ids',
                 'commercial_partner_id.child_ids.sale_order_ids',
                 'commercial_partner_id.child_ids.sale_order_ids.state',
                 'commercial_partner_id.invoice_ids',
                 'commercial_partner_id.child_ids.invoice_ids')
    def _compute_prospect(self):
        for record in self:
            sale_ids = (
                record.commercial_partner_id.sale_order_ids +
                record.commercial_partner_id.mapped(
                    'child_ids.sale_order_ids'))
            invoice_ids = (
                record.commercial_partner_id.invoice_ids +
                record.commercial_partner_id.mapped(
                    'child_ids.invoice_ids'))
            record.prospect = (
                not sale_ids.filtered(
                    lambda r: r.state not in
                    ('draft', 'sent', 'cancel')) and
                not invoice_ids.filtered(
                    lambda r: r.type in ('out_invoice', 'out_refund')))

    prospect = fields.Boolean(
        string='Prospect', compute='_compute_prospect', default=False,
        store=True, compute_sudo=True)
