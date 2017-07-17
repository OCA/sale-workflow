# -*- coding: utf-8 -*-
from openerp import models, api


class sale_order(models.Model):
    _inherit = "sale.order"

    @api.multi
    def check_credit_limit_ok(self):
        self.ensure_one()
        # por compatibilidad con el modulo de sale_order_type_invoice_policy
        if self._context.get('by_pass_credit_limit', False):
            return True

        domain = [
            ('order_id.id', '!=', self.id),
            ('order_id.partner_id', '=', self.partner_id.id),
            # buscamos las que estan a facturar o las no ya que nos interesa
            # la cantidad total y no solo la facturada. Esta busqueda ayuda
            # a que no busquemos en todo lo que ya fue facturado al dope
            ('invoice_status', 'in', ['to invoice', 'no']),
            ('order_id.state', 'in', ['sale', 'done']),
        ]
        order_lines = self.env['sale.order.line'].search(domain)

        # We sum from all the sale orders that are aproved, the sale order
        # lines that are not yet invoiced
        to_invoice_amount = 0.0
        for line in order_lines:
            # not_invoiced is different from native qty_to_invoice because
            # the last one only consider to_invoice lines the ones
            # that has been delivered or are ready to invoice regarding
            # the invoicing policy. Not_invoiced consider all
            not_invoiced = line.product_uom_qty - line.qty_invoiced
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(
                price, line.order_id.currency_id,
                not_invoiced,
                product=line.product_id, partner=line.order_id.partner_id)
            to_invoice_amount += taxes['total_included']

        # We sum from all the invoices lines that are in draft and not linked
        # to a sale order
        domain = [
            ('invoice_id.partner_id', '=', self.partner_id.id),
            ('invoice_id.state', '=', 'draft'),
            ('sale_line_ids', '=', False)]
        draft_invoice_lines = self.env['account.invoice.line'].search(domain)
        draft_invoice_lines_amount = 0.0
        for line in draft_invoice_lines:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(
                price, line.invoice_id.currency_id,
                line.quantity,
                product=line.product_id, partner=line.invoice_id.partner_id)
            draft_invoice_lines_amount += taxes['total_included']

        available_credit = self.partner_id.credit_limit - \
            self.partner_id.credit - \
            to_invoice_amount - draft_invoice_lines_amount
        if self.amount_total > available_credit:
            return False
        return True
