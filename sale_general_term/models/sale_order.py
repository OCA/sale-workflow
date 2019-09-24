# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_id_general_terms(self):
        Terms = self.env['sale.general.term']
        self.general_term_id = Terms.get_partner_general_terms(
            self.partner_id)

    general_term_id = fields.Many2one(
        'sale.general.term',
        string="General Terms",
        domain=[('is_enabled', '=', True)],
    )
