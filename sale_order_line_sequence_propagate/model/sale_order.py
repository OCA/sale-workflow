# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields, orm


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False,
                                         context=None):
        res = super(SaleOrder, self)._prepare_order_line_invoice_line(
            cr, uid, line, account_id=account_id, context=context)
        res['order_line_sequence'] = line.sequence
        return res

    def _prepare_order_line_move(self, cr, uid, order, line, picking_id,
                                 date_planned, context=None):
        res = super(SaleOrder, self)._prepare_order_line_move(cr, uid,
                                                              order, line,
                                                              picking_id,
                                                              date_planned,
                                                              context=context)
        res['order_line_sequence'] = line.sequence
        return res
