# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'
    _columns = {
        'sequence': fields.integer('Sequence',
                                   help="Gives the sequence of this line when "
                                        "displaying the purchase order."),
        }
    _order = 'order_id desc, sequence, id'
    _defaults = {'sequence': 10,
                 }


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        res = super(purchase_order, self)._prepare_inv_line(cr, uid,
                                                            account_id,
                                                            order_line, context)
        res['sequence'] = order_line.sequence
        return res

    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, context=None):
        res = super(purchase_order, self)._prepare_order_line_move(cr, uid,
                                                                   order,
                                                                   line,
                                                                   picking_id)
        res['sequence'] = line.sequence
        return res


class purchase_line_invoice(orm.TransientModel):
    _inherit = 'purchase.order.line_invoice'

    def makeInvoices(self, cr, uid, ids, context=None):
        invoice_line_obj = self.pool.get('account.invoice.line')
        purchase_line_obj = self.pool.get('purchase.order.line')
        res = super(purchase_line_invoice, self).makeInvoices(cr, uid, ids, context)
        invoice_ids = eval(res['domain'])[0][-1]  # OMG :-(
        invoice_line_ids = invoice_line_obj.search(cr, uid,
                                                   [('invoice_id', 'in', invoice_ids)],
                                                   context=context)
        for invoice_line in invoice_line_obj.browse(cr, uid,
                                                    invoice_line_ids,
                                                    context=context):
            order_line_ids = purchase_line_obj.search(cr, uid,
                                                      [('invoice_lines', '=', invoice_line.id)],
                                                      context=context)
            if not order_line_ids:
                continue
            record_data = purchase_line_obj.read(cr, uid,
                                                 order_line_ids[0],
                                                 ['sequence'],
                                                 context=context)
            order_line_seq = record_data['sequence']
            if not invoice_line.sequence:
                invoice_line.write({'sequence': order_line_seq})
        return res

