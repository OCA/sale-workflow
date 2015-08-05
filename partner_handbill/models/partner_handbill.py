# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends('sale_order_ids', 'sale_order_ids.state')
    def _sale_order_count2(self):
        for line in self.sale_order_ids:
            if line.state in ('done', 'cancel'):
                self.handbill = True

    handbill = fields.Boolean(string='Handbill', readonly=True,
                              compute='_sale_order_count2', store=True)
