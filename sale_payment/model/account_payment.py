# -*- coding: utf-8 -*-
# Copyright (C) 2016  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_id = fields.Many2one(
        'sale.order',
        string='Sales Order')

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        if not self.env.context.get('active_model') == 'sale.order':
            return rec
        sale_id = self.env.context.get('active_id')
        sale = self.env['sale.order'].browse(sale_id)

        rec['communication'] = sale.name
        rec['currency_id'] = sale.currency_id.id
        rec['payment_type'] = 'inbound'
        rec['partner_type'] = 'customer'
        rec['partner_id'] = sale.partner_invoice_id.id
        rec['amount'] = sale.residual
        rec['sale_id'] = sale.id
        return rec

    def _get_counterpart_move_line_vals(self, invoice=False):
        res = super(AccountPayment, self)._get_counterpart_move_line_vals(
            invoice=invoice)
        sale_ids = []
        if invoice:
            for inv in invoice:
                for invoice_line in invoice.invoice_line_ids:
                    sale_ids += [
                        sl.order_id.id for sl in invoice_line.sale_line_ids
                        if sl.order_id.id not in sale_ids]
        elif self.sale_id:
            sale_ids.append(self.sale_id.id)
        res['sale_ids'] = [(6, 0, sale_ids)]
        return res
