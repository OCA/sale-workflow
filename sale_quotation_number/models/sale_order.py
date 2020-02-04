# © 2010-2012 Andy Lu <andy.lu@elico-corp.com> (Elico Corp)
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 valentin vinagre  <valentin.vinagre@qubiq.es> (QubiQ)
# Richard deMeester <richard.demeester@willdooit.com> (Willdoo IT)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        company = self.env['res.company']._company_default_get('sale.order')
        if not company.keep_name_so:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sale.quotation') or _('New')
        return super().create(vals)

    @api.multi
    def action_confirm(self):
        if super().action_confirm():
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
