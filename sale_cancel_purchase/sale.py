# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from osv import orm

class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def action_cancel(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        po_line_obj = self.pool.get('purchase.order.line')
        for order_id in ids:
            order = self.browse(cr, uid, [order_id], context=context)[0]
            po_line_ids = po_line_obj.search(
                cr, uid, [('sale_order_id','=',order_id)], context=context
            )
            for po_line in po_line_obj.browse(cr, uid, po_line_ids,
                                                context=context):
                if not order.cancel_logs:
                    cancel_logs = ""
                else:
                    cancel_logs = order.cancel_logs
                if po_line.order_id.state in ['draft']:
                    po_line_obj.unlink(cr, uid, po_line_ids, context=context)
                    self.write(
                        cr, uid, order_id,
                        {'cancel_logs':cancel_logs + "<p>Number of deleted \
                            lines in Purchase Orders : %d" % len(po_line_ids)},
                        context=context
                    )
                    picking_ids = picking_obj.search(
                        cr, uid, [('purchase_id','=',order_id)], context=context)
                    picking_obj.action_cancel(cr, uid, picking_ids, context=context)
                    self.write(
                        cr, uid, order_id,
                        {'cancel_logs':cancel_logs + "<p>Cancel %d incoming \
                            pickings" % len(picking_ids)},
                        context=context
                    )
                else:
                    self.write(
                        cr, uid, order_id,
                        {'cancel_logs': cancel_logs + "<p>Impossible to cancel Sale\
                        Order. State is %s" % order.state},
                        context=context
                    )
        return super(SaleOrder, self).action_cancel(
            cr, uid, ids, context=context
        )


