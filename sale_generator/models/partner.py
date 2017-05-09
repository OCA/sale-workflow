# coding: utf-8
#  @author Sébastien BEAU <sebastien.beau@akretion.com>
#  @author Abdessamad HILALI <abdessamad.hilali@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def close_from_customer_wizard(self):
        action = self.env.ref(
            'sale_generator.act_sale_generator_2_sale_order').read()
        action['res_id'] = self.env.context.get('from_generator_id')
        return action

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        generator_id = self.env.context.get('from_generator_id')
        if generator_id:
            generator = self.env['sale.generator'].browse(generator_id)
            generator.write({'partner_ids': [(4, res.id, 0)]})
        return res
