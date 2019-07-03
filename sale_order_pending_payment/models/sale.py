# -*- coding: utf-8 -*-
# Copyright 2018 PlanetaTIC - Lluís Rovira <lrovira@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total', 'order_line.price_unit')
    def _amount_deposit(self):
        for order in self:
            order.amount_tax = amount_deposit = amount_invoiced = \
                amount_residual = amount_deposit_paid = 0.0
            for line in order.order_line:
                if line.product_id.id == order.env['ir.values'].get_default(
                            'sale.config.settings',
                            'deposit_product_id_setting') and \
                        line.product_uom_qty == 0:
                    amount_deposit += line.price_unit * line.qty_invoiced
                    for invoice_line in line.invoice_lines:
                        if invoice_line.invoice_id.residual == 0 and \
                            invoice_line.invoice_id.state not in \
                                ('draft', 'cancel'):
                            amount_deposit_paid += \
                                line.price_unit * line.qty_invoiced
            for invoice in order.invoice_ids:
                if invoice.state not in ('draft', 'cancel'):
                    amount_invoiced += invoice.amount_total
                    amount_residual += invoice.residual
            if amount_invoiced == order.amount_total:
                total_pending = amount_residual
            else:
                total_pending = \
                    order.amount_total - (amount_invoiced - amount_residual)
            order.update({
                'amount_deposit': amount_deposit,
                'amount_paid':
                    amount_invoiced - amount_residual - amount_deposit_paid,
                'amount_total_pending': total_pending - amount_deposit +
                    amount_deposit_paid,
            })

    amount_deposit = fields.Monetary(string='Deposit', readonly=True,
                                     compute='_amount_deposit',
                                     track_visibility='always')
    amount_paid = fields.Monetary(string='Paid', readonly=True,
                                  compute='_amount_deposit',
                                  track_visibility='always')
    amount_total_pending = fields.Monetary(string='Total Pending',
                                           readonly=True,
                                           compute='_amount_deposit',
                                           track_visibility='always')
