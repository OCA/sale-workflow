# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from osv import orm, fields

class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def action_cancel(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        for order_id in ids:
            order_name = self.read(cr, uid, [order_id], fields=['name'])[0]
            cancel_logs = self.read(cr, uid, [order_id], fields=['cancel_logs'])[0]
            picking_ids = picking_obj.search(
                cr, uid, [('origin','=',order_name['name'])], context=context
            )
            picking_obj.action_cancel(cr, uid, picking_ids, context=context)
            for picking in picking_obj.browse(cr, uid, picking_ids,
                                                context=context):
                print cancel_logs
                self.write(
                    cr, uid, [order_id],
                    {'cancel_logs': cancel_logs['cancel_logs'] + "<p>Canceled picking out: %s</p>" % picking.name},
                    context=context
                )
                print self.browse(cr, uid, order_id, context=context).cancel_logs
        return super(SaleOrder, self).action_cancel(
            cr, uid, ids, context=context
        )

    _columns = {
        'cancel_logs': fields.html("Cancellation Logs"),
    }
