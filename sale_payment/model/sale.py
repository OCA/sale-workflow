# -*- coding: utf-8 -*-
# Copyright (C) 2016  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    def _get_residual(self):
        paid_amount = 0.0
        for line in self.payment_ids:
            amount = line.credit - line.debit
            if line.currency_id != self.currency_id:
                from_currency = (line.currency_id and
                                 line.currency_id.with_context(
                                     date=line.date)) or \
                    line.company_id.currency_id.with_context(
                        date=line.date)
                amount = from_currency.compute(amount, self.currency_id)
            paid_amount += amount
        self.residual = self.amount_total - paid_amount
        self.amount_paid = paid_amount

    payment_ids = fields.Many2many(
        comodel_name='account.move.line',
        string='Payments Entries',
        domain=[('account_id.internal_type', '=', 'receivable')],
        copy=False,
    )
    residual = fields.Float(
        compute='_get_residual',
        digits_compute=dp.get_precision('Account'))
    amount_paid = fields.Float(
        compute='_get_residual',
        digits_compute=dp.get_precision('Account'))
