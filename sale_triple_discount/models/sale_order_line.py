# -*- coding: utf-8 -*-
# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import openerp.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount1 = fields.Float(
        'Discount 1 (%)',
        digits=dp.get_precision('Discount'),
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
    )
    discount2 = fields.Float(
        'Discount 2 (%)',
        digits=dp.get_precision('Discount'),
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
    )
    discount3 = fields.Float(
        'Discount 3 (%)',
        digits=dp.get_precision('Discount'),
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
    )
    discount = fields.Float(compute='get_discount')

    @api.multi
    @api.depends('discount1', 'discount2', 'discount3')
    def get_discount(self):
        for line in self:
            discount_factor = 1.0
            for discount in [line.discount1, line.discount2, line.discount3]:
                discount_factor = (
                    discount_factor * ((100.0 - discount) / 100.0))
            line.discount = 100.0 - (discount_factor * 100.0)

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'discount1': self.discount1,
            'discount2': self.discount2,
            'discount3': self.discount3})
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        partner = self.order_id.partner_id
        self.discount1 = partner.default_discount1
        self.discount2 = partner.default_discount2
        self.discount3 = partner.default_discount3
