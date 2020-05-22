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
        # allocate new number before confirm - as reference on MTO orders
        # should be the sale number, not the quote number
        company = self.env['res.company']. \
            _company_default_get('sale.order')
        for order in self:
            if order.state in ('draft', 'sent') and not company.keep_name_so:
                if order.origin and order.origin != '':
                    quo = order.origin + ', ' + order.name
                else:
                    quo = order.name
                order.write({
                    'origin': quo,
                    'name': self.env['ir.sequence'].next_by_code(
                        'sale.order')
                })
        return super().action_confirm()

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if not 'origin' in default:
            default['origin'] = False
        return super().copy(default)
