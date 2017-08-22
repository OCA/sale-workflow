# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = ['onchange.mixin', 'sale.order']
    _name = 'sale.order'

    covenant_id = fields.Many2one(
        comodel_name='sale.covenant', string='Covenant',
        help="Covenant drive commitments on markets")

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """ Update 'Covenant' fields when the partner is changed:
        """
        res = super(SaleOrder, self).onchange_partner_id()
        if not self.partner_id:
            self.covenant_id = False,
        else:
            # covenant can be defined on contact or parent
            self.covenant_id = (self.partner_id.covenant_id or
                                self.partner_id.parent_id.covenant_id)
        return res
