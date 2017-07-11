# -*- coding: utf-8 -*-

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    percent = fields.Float(
        string='Percent',
        compute='_compute_percent')

    @api.depends('margin', 'amount_untaxed')
    def _compute_percent(self):
        for order in self:
            percent = 0
            if order.margin and order.amount_untaxed:
                percent = (order.margin / order.amount_untaxed) * 100
            order.percent = percent
