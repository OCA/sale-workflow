# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


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
