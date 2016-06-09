# -*- coding: utf-8 -*-
# Copyright (C) 2014-Today: Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
from openerp.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.depends(
        'price_unit', 'quantity', 'uos_id', 'invoice_line_tax_id',
        'price_subtotal', 'invoice_id.currency_id')
    def _get_amount_line_tax(self):
        for line in self:
            currency = line.invoice_id.currency_id
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_id.compute_all(
                price, line.quantity, product=line.product_id,
                partner=line.invoice_id.partner_id)
            line.price_subtotal_taxinc = currency.round(
                taxes['total_included'])
            line.vat_subtotal = currency.round(
                (taxes['total_included'] - taxes['total']))

    price_subtotal_taxinc = fields.Float(
        compute='_get_amount_line_tax', string='Total Tax Incl.',
        digits_compute=dp.get_precision('Sale Price'), store=True,
        multi='tax_details')

    vat_subtotal = fields.Float(
        compute='_get_amount_line_tax', string='Taxes Amount',
        digits_compute=dp.get_precision('Sale Price'), store=True,
        multi='tax_details')
