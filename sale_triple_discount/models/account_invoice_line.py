# -*- coding: utf-8 -*-
# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import openerp.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def _default_discount1(self):
        default_discount1 = 0.0
        partner_id = self.env.context.get('partner_id', False)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            default_discount1 = partner.default_discount1
        return default_discount1

    @api.model
    def _default_discount2(self):
        default_discount2 = 0.0
        partner_id = self.env.context.get('partner_id', False)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            default_discount2 = partner.default_discount2
        return default_discount2

    @api.model
    def _default_discount3(self):
        default_discount3 = 0.0
        partner_id = self.env.context.get('partner_id', False)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            default_discount3 = partner.default_discount3
        return default_discount3

    discount1 = fields.Float(
        'Discount 1 (%)',
        digits=dp.get_precision('Discount'),
        default=_default_discount1,
    )
    discount2 = fields.Float(
        'Discount 2 (%)',
        digits=dp.get_precision('Discount'),
        default=_default_discount2,
    )
    discount3 = fields.Float(
        'Discount 3 (%)',
        digits=dp.get_precision('Discount'),
        default=_default_discount3,
    )
    discount = fields.Float(
        compute='get_discount',
        store=True,
        readonly=True,
    )

    @api.multi
    @api.depends('discount1', 'discount2', 'discount3')
    def get_discount(self):
        for line in self:
            discount_factor = 1.0
            for discount in [line.discount1, line.discount2, line.discount3]:
                discount_factor = (
                    discount_factor * ((100.0 - discount) / 100.0))
            line.discount = 100.0 - (discount_factor * 100.0)
