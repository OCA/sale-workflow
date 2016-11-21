# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _prepare_refund(self, invoice, date=None, period_id=None,
                        description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(
            invoice, date, period_id, description, journal_id)
        if invoice.origin:
            orders = self.env['sale.order'].search(
                [('name', '=', invoice.origin)])
            journal = False
            if orders:
                journal = orders[0].type_id.refund_journal_id
            else:
                pickings = self.env['stock.picking'].search(
                    [('name', '=', invoice.origin)])
                if pickings:
                    journal = pickings[0].sale_id.type_id.refund_journal_id
            if journal:
                values['journal_id'] = journal.id
        return values
