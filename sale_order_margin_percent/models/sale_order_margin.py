# -*- coding: utf-8 -*-

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    percent = fields.Float(
        string='Percent',
        compute='_compute_percent')

    @api.depends('margin', 'amount_untaxed')
    def _compute_percent(self):
        if self.margin and self.amount_untaxed:
            self.percent = (self.margin / self.amount_untaxed) * 100
