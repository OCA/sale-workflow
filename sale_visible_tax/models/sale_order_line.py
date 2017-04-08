# -*- coding: utf-8 -*-
# Copyright (C) 2014-Today: Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
from openerp.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.depends(
        'price_unit', 'product_uom_qty', 'product_uos_qty', 'tax_id',
        'price_subtotal', 'product_uom', 'product_uos')
    def _get_amount_line_tax(self):
        order_obj = self.env['sale.order']
        for line in self:
            amount_tax_line = order_obj._amount_line_tax(line)
            line.vat_subtotal = amount_tax_line
            line.price_subtotal_taxinc = amount_tax_line + line.price_subtotal

    price_subtotal_taxinc = fields.Float(
        compute='_get_amount_line_tax', string='Total Tax Incl.',
        digits_compute=dp.get_precision('Sale Price'), store=True,
        multi='tax_details')

    vat_subtotal = fields.Float(
        compute='_get_amount_line_tax', string='Taxes Amount',
        digits_compute=dp.get_precision('Sale Price'), store=True,
        multi='tax_details')
