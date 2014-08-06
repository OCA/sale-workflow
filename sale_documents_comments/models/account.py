# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import orm, fields


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'sale_comment': fields.text('Internal comments'),
    }

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
                            date_invoice=False, payment_term=False,
                            partner_bank_id=False, company_id=False,
                            context=None):
        val = super(AccountInvoice, self).onchange_partner_id(
            cr, uid, ids, type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id, context=context)
        if partner_id:
            partner_obj = self.pool['res.partner']
            partner = partner_obj.browse(cr, uid, partner_id, context=context)
            val['value']['sale_comment'] = partner.invoice_comment
        return val
