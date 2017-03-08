# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    section_partner_invoice_id = fields.Many2one(
        comodel_name='res.partner', related='team_id.section_partner_invoice_id',
        string='Invoice Address', readonly=True,
        help="Invoice address for current sales order.")

    @api.model
    def create(self, vals):
        team_id = vals.get('team_id', False)
        if team_id:
            section = self.env['crm.case.section'].browse(team_id)
            if section.section_partner_invoice_id:
                vals['partner_invoice_id'] = (section.
                                              section_partner_invoice_id.id)
        order = super(SaleOrder, self).create(vals)
        return order

    @api.multi
    def write(self, vals):
        if 'team_id' in vals:
            team_id = vals.get('team_id')
            section = self.env['crm.case.section'].browse(team_id)
            if section.section_partner_invoice_id:
                vals.update({
                    'partner_invoice_id': section.section_partner_invoice_id.id
                })
        return super(SaleOrder, self).write(vals)

    @api.multi
    def update(self, vals):
        if self.team_id.section_partner_invoice_id:
            vals['partner_invoice_id'] = \
                self.team_id.section_partner_invoice_id
        return super(SaleOrder, self).update(vals)
