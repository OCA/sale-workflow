# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends('sale_order_ids', 'sale_order_ids.state')
    def _compute_handbill(self):
        self.handbill = not self.sale_order_ids.filtered(
            lambda r: r.state not in ('draft', 'sent', 'cancel'))

    handbill = fields.Boolean(string='Handbill', readonly=True,
                              compute='_compute_handbill', store=True)
