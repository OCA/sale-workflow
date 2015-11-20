# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of sale_order_partial_advance,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     sale_order_partial_advance is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     sale_order_partial_advance is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with sale_order_partial_advance.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    @api.depends('invoice_ids')
    def _compute_advance_amounts(self):
        advance_amount, advance_amount_used = 0, 0
        adv_product_id =\
            self.env['sale.advance.payment.inv']._get_advance_product()
        for invoice in self.invoice_ids:
            if invoice.state == 'cancel':
                continue
            advance_amount += sum([line.price_subtotal
                                  for line in invoice.invoice_line
                                  if (line.product_id.id == adv_product_id
                                      and line.price_subtotal > 0)])
            advance_amount_used -= sum([line.price_subtotal
                                        for line in invoice.invoice_line
                                        if (line.product_id.id ==
                                            adv_product_id
                                            and line.price_subtotal < 0)])
        self.advance_amount_available = advance_amount - advance_amount_used
        self.advance_amount = advance_amount
        self.advance_amount_used = advance_amount_used

    @api.model
    def _prepare_invoice(self, order, lines):
        adv_product_id =\
            self.env['sale.advance.payment.inv']._get_advance_product()
        for invoice_line in self.env['account.invoice.line'].browse(lines):
            if invoice_line.product_id.id == adv_product_id:
                if - invoice_line.price_unit > order.advance_amount_available:
                    invoice_line.write(
                        {'price_unit': - order.advance_amount_available})
        return super(SaleOrder, self)._prepare_invoice(order, lines)

    advance_amount = fields.Float('Advance Amount',
                                  compute='_compute_advance_amounts')
    advance_amount_available = fields.Float('Advance Available',
                                            compute='_compute_advance_amounts')
    advance_amount_used = fields.Float('Advance Used',
                                       compute='_compute_advance_amounts')
