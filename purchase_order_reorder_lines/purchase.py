# -*- coding: utf-8 -*-
#
#
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
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
#

from openerp import models, api, fields
from openerp.tools.safe_eval import safe_eval


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _order = 'order_id desc, sequence, id'

    @api.model
    def _get_sequence(self):
        last_sequence = 0
        return last_sequence

    sequence = fields.Integer(default=_get_sequence,
                              help="Gives the sequence of this line when "
                                   "displaying the purchase order.")


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_inv_line(self, account_id, order_line):
        res = super(PurchaseOrder, self)._prepare_inv_line(
            account_id,
            order_line,
            )
        res['sequence'] = order_line.sequence
        return res

    @api.model
    def _prepare_order_line_move(self, order, order_line,
                                 picking_id, group_id):
        res = super(PurchaseOrder, self)._prepare_order_line_move(
            order,
            order_line,
            picking_id,
            group_id)
        if res:
            res[0]['sequence'] = order_line.sequence
        return res


class PurchaseLineInvoice(models.TransientModel):
    _inherit = 'purchase.order.line_invoice'

    @api.multi
    def makeInvoices(self):
        invoice_line_obj = self.env['account.invoice.line']
        purchase_line_obj = self.env['purchase.order.line']
        res = super(PurchaseLineInvoice, self).makeInvoices()

        invoice_ids = []
        for field, op, val in safe_eval(res['domain']):
            if field == 'id':
                invoice_ids = val
                break

        invoice_lines = invoice_line_obj.search(
            [('invoice_id', 'in', invoice_ids)])
        for invoice_line in invoice_lines:
            order_lines = purchase_line_obj.search(
                [('invoice_lines', '=', invoice_line.id)],
                )
            if not order_lines:
                continue

            if not invoice_line.sequence:
                invoice_line.write({'sequence': order_lines.sequence})

        return res
