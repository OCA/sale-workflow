# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        if not vals.get('source_id'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if partner.source_id:
                vals['source_id'] = partner.source_id.id
        return super().create(vals)
