# coding: utf-8
#  @author Sébastien BEAU <sebastien.beau@akretion.com>
#  @author Abdessamad HILALI <abdessamad.hilali@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def close_from_customer_wizard(self):
        generator_id = self.env.context.get('from_generator_id')
        action = self.env.ref('sale_generator.act_sale_generator_2_sale_order')
        action['res_id'] = generator_id
        return action

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        generator_id = self.env.context.get('from_generator_id')
        if generator_id:
            generator = self.env['sale.generator'].browse(generator_id)
            generator.partner_ids += res

        return res

    def add_new_generated_partner(self):

        return {'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'name': u"New Customer",
                'id': self.env.ref('base.view_partner_form').id,
                'view_mode': 'form',
                'target': 'new',
                }
