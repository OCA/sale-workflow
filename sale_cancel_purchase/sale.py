# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp.osv import orm
from openerp.tools.translate import _


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def action_cancel(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        po_line_obj = self.pool.get('purchase.order.line')
        cancel_ids = []
        for order in self.browse(cr, uid, ids, context=context):
            po_line_ids = po_line_obj.search(
                cr, uid, [('sale_order_id', '=', order.id)], context=context
            )
            cancel = True
            line_to_cancel = []
            for po_line in po_line_obj.browse(cr, uid, po_line_ids,
                                              context=context):
                if po_line.state in ['draft']:
                    line_to_cancel.append(po_line.id)
                else:
                    log = _("Impossible to cancel Purchase Order Line in %s "
                            "for product %s because Line's state is in %s")
                    log %= (po_line.order_id.name, po_line.product_id.name,
                            po_line.state)
                    order.add_logs(log, False)
            if line_to_cancel:
                po_line_obj.unlink(cr, uid, line_to_cancel, context=context)
                log = _("Number of deleted lines in Purchase Order: "
                        "%s") % len(po_line_ids)
                order.add_logs(log, True)
            if cancel:
                cancel_ids.append(order.id)
        return super(SaleOrder, self).action_cancel(
            cr, uid, cancel_ids, context=context
        )
