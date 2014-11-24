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
        for order in self.browse(cr, uid, ids, context=context):
            po_line_ids = po_line_obj.search(
                cr, uid, [('sale_order_id', '=', order.id)], context=context
            )
            for po_line in po_line_obj.browse(cr, uid, po_line_ids,
                                              context=context):
                if po_line.state in ['draft']:
                    po_line_obj.unlink(cr, uid, [po_line.id], context=context)
                    log_line = "<p>Number of deleted lines in Purchase \
                        Orders: %d</p>" % len(po_line_ids)
                    picking_ids = picking_obj.search(
                        cr, uid, [('purchase_id', '=', po_line.order_id.id)],
                        context=context
                    )
                    for picking in picking_obj.browse(cr, uid, picking_ids,
                                                      context=context):
                        if picking.state in ['assigned', 'confirmed', 'draft']:
                            picking.action_cancel()
                            log = "<p>Canceled picking in: %s</p>" % \
                                picking.name
                        else:
                            log = "<p>Can't cancel picking in: %s</p>" \
                                % picking.name
                        order.add_logs(log)
                else:
                    log_line = "<p>Impossible to cancel Purchase Order Line \
                        for product %s because Line's state is in %s" % \
                        (po_line.product_id, po_line.state)
                order.add_logs(log_line)
        return super(SaleOrder, self).action_cancel(
            cr, uid, ids, context=context
        )
