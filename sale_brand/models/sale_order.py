# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    brand_id = fields.Many2one(
        'res.partner', string='Brand', domain="[('type', '=', 'brand')]",
        help="Brand to use for this sale")

    @api.multi
    def _prepare_invoice(self):
        for order in self:
            invoice_vals = super(SaleOrder, order)._prepare_invoice()
            invoice_vals.update({
                'brand_id': order.brand_id.id,
            })
        return invoice_vals
