# -*- coding: utf-8 -*-
# © 2010-2012 Andy Lu <andy.lu@elico-corp.com> (Elico Corp)
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 valentin vinagre  <valentin.vinagre@qubiq.es> (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    keep_name_so = fields.Boolean(
        string="Use Same Enumeration",
        help="If this is unchecked, quotations use a different sequence from "
             "sale orders", default=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    keep_name_so = fields.Boolean(related='company_id.keep_name_so')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        default['name'] = '/'
        if self.origin and self.origin != '':
            default['origin'] = self.origin + ', ' + self.name
        else:
            default['origin'] = self.name
        return super(SaleOrder, self).copy(default)

    @api.model
    def create(self, vals):
        company = self.env['res.company']._company_default_get('sale.order')
        if not company.keep_name_so:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sale.quotation') or '/'
        return super(SaleOrder, self).create(vals)

    @api.multi
    def action_confirm(self):
        if super(SaleOrder, self).action_confirm():
            company = self.env['res.company']. \
                _company_default_get('sale.order')
            for order in self:
                if order.state == 'sale' and not company.keep_name_so:
                    if order.origin and order.origin != '':
                        quo = order.origin + ', ' + order.name
                    else:
                        quo = order.name
                    order.write({
                        'origin': quo,
                        'name': self.env['ir.sequence'].next_by_code(
                            'sale.order')
                    })
        return True
