# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


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
        for partner in self:
            sale_ids = (
                partner.commercial_partner_id.sale_order_ids +
                partner.commercial_partner_id.mapped(
                    'child_ids.sale_order_ids'))
            invoice_ids = (
                partner.commercial_partner_id.invoice_ids +
                partner.commercial_partner_id.mapped(
                    'child_ids.invoice_ids'))
            partner.prospect = (
                not sale_ids.filtered(
                    lambda r: r.state not in
                    ('draft', 'sent', 'cancel')) and
                not invoice_ids.filtered(
                    lambda r: r.type in ('out_invoice', 'out_refund')))

    prospect = fields.Boolean(
        'Prospect', compute='_compute_prospect',
        store=True)
