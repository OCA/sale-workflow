# -*- coding: utf-8 -*-
# Copyright 2018 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_cancel(self):
        for order in self:
            order.cancel_draft_invoice()
        return super(SaleOrder, self).action_cancel()

    def cancel_draft_invoice(self):
        for invoice in self.invoice_ids:
            if not invoice.number and (invoice.state == 'draft' or invoice.state == 'proforma' or invoice.state == 'proforma2'):
                invoice.signal_workflow('invoice_cancel')

    @api.multi
    def write(self, values):
        for order in self:
            if 'order_line' in values:
                order.cancel_draft_invoice()
        res = super(SaleOrder, self).write(values)
        return res
