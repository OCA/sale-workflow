# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_type_id = fields.Many2one(
        comodel_name='sale.order.type', string='Sale Type')

    @api.multi
    def _prepare_refund(self, invoice, date=None, period_id=None,
                        description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(
            invoice, date, period_id, description, journal_id)
        if invoice.type in ['out_invoice', 'out_refund'] and\
                invoice.origin:
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

    @api.multi
    def onchange_partner_id(
        self, type, partner_id, date_invoice=False,
        payment_term=False, partner_bank_id=False,
        company_id=False
    ):
        res = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if partner.sale_type:
                res['value'].update({
                    'type_id': partner.sale_type.id,
                })
        return res

    @api.onchange('sale_type_id')
    def onchange_sale_type_id(self):
        if self.sale_type_id.payment_term_id:
            self.payment_term = self.sale_type_id.payment_term_id.id
        if self.sale_type_id.journal_id:
            self.journal_id = self.sale_type_id.journal_id.id
