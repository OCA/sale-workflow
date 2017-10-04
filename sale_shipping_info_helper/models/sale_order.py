# -*- coding: utf-8 -*-
# © 2017-To Day Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author: Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
import openerp.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_amount_total = fields.Float(
        compute='_compute_shipping',
        dp=dp.get_precision('Account'),
        store=True)
    shipping_amount_untaxed = fields.Float(
        compute='_compute_shipping',
        dp=dp.get_precision('Account'),
        store=True)
    shipping_amount_tax = fields.Float(
        compute='_compute_shipping',
        dp=dp.get_precision('Account'),
        store=True)
    item_amount_total = fields.Float(
        compute='_compute_shipping',
        dp=dp.get_precision('Account'),
        store=True)
    item_amount_untaxed = fields.Float(
        compute='_compute_shipping',
        dp=dp.get_precision('Account'),
        store=True)
    item_amount_tax = fields.Float(
        compute='_compute_shipping',
        dp=dp.get_precision('Account'),
        store=True)

    @api.depends('amount_total', 'amount_untaxed')
    def _compute_shipping(self):
        for record in self:
            record.shipping_amount_untaxed = 0
            record.shipping_amount_total = 0
            record.shipping_amount_tax = 0
            for line in record.order_line:
                if line['is_delivery']:
                    record.shipping_amount_untaxed = line['price_subtotal']
                    record.shipping_amount_total = line['price_total']
                    record.shipping_amount_tax = line['price_tax']
        for key in ['amount_total', 'amount_untaxed', 'amount_tax']:
            record['item_%s' % key] = record[key] - record['shipping_%s' % key]
