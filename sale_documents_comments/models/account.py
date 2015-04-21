# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_comment = fields.Text(string='Internal comments')

    @api.multi
    def onchange_partner_id(self, invoice_type, partner_id,
                            date_invoice=False, payment_term=False,
                            partner_bank_id=False, company_id=False):
        val = super(AccountInvoice, self).onchange_partner_id(
            invoice_type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if partner_id:
            partner_obj = self.env['res.partner']
            partner = partner_obj.browse(partner_id)
            comment = partner.invoice_comment or ''
            if partner.parent_id:
                comment += '\n%s' % (partner.parent_id.invoice_comment or '')
            val['value']['sale_comment'] = comment
        return val
