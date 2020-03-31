# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        val = self.env['ir.config_parameter'].sudo().get_param(
            'sale.group_sale_order_dates')
        res.update({'group_sale_order_dates': val})
        return res
