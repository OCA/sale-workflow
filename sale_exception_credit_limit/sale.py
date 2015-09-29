# -*- coding: utf-8 -*-
from openerp import models, api


class sale_order(models.Model):
    _inherit = "sale.order"

    @api.multi
    def check_credit_limit_ok(self):
        self.ensure_one()
        if self.order_policy == 'prepaid':
            return True

        # We sum from all the sale orders that are aproved, the sale order
        # lines that are not yet invoiced
        domain = [('order_id.partner_id', '=', self.partner_id.id),
                  ('invoiced', '=', False),
                  ('order_id.state', 'not in', ['draft', 'cancel', 'sent'])]
        order_lines = self.env['sale.order.line'].search(domain)
        none_invoiced_amount = sum(order_lines.mapped('price_subtotal'))

        # We sum from all the invoices that are in draft the total amount
        domain = [
            ('partner_id', '=', self.partner_id.id), ('state', '=', 'draft')]
        draft_invoices = self.env['account.invoice'].search(domain)
        draft_invoices_amount = sum(draft_invoices.mapped('amount_total'))

        available_credit = self.partner_id.credit_limit - \
            self.partner_id.credit - \
            none_invoiced_amount - draft_invoices_amount

        if self.amount_total > available_credit:
            return False
        return True
