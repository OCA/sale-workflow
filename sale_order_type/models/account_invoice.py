# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None,
                        date=None, description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice, date, description, journal_id)
        if invoice.origin:
            orders = self.env['sale.order'].search(
                [('name', '=', invoice.origin)], limit=1)
            journal = False
            if orders:
                journal = orders.type_id.refund_journal_id
            else:
                pickings = self.env['stock.picking'].search(
                    [('name', '=', invoice.origin)], limit=1)
                if pickings:
                    journal = pickings.sale_id.type_id.refund_journal_id
            if journal:
                values['journal_id'] = journal.id
        return values
