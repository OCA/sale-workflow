# -*- coding: utf-8 -*-
# Copyright 2018 PlanetaTIC - Lluís Rovira <lrovira@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total', 'order_line.price_unit')
    def _amount_deposit(self):
        for order in self:
            order.amount_tax = amount_deposit = 0.0
            for line in order.order_line:
                amount_deposit += line.price_unit*line.qty_invoiced if \
                    line.product_id.id == order.env['ir.values'].get_default(
                            'sale.config.settings',
                            'deposit_product_id_setting') else 0
            order.update({
                'amount_deposit': amount_deposit,
                'amount_total_pending': order.amount_total - amount_deposit,
            })

    amount_deposit = fields.Monetary(string='Deposit', readonly=True,
                                     compute='_amount_deposit',
                                     track_visibility='always')
    amount_total_pending = fields.Monetary(string='Total Pending',
                                           readonly=True,
                                           compute='_amount_deposit',
                                           track_visibility='always')
