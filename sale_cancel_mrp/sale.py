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
        mrp_prod_obj = self.pool.get('mrp.production')
        picking_obj = self.pool.get('stock.picking')
        mo_ids = mrp_prod_obj.search(
            cr, uid, [('sale_order_id','in',ids)], context=context
        )
        picking_ids = False
        for mo in mrp_prod_obj.browse(cr, uid, mo_ids, context=context):
            self.write(
                cr, uid, mo.sale_order_id.id,
                {'cancel_logs': mo.sale_order_id.cancel_logs + "<p>Cancel picking on %s</p>" % mo.name},
                context=context
            )
            picking_obj.action_cancel(cr, uid, [mo.picking_id.id], context=context)
            mrp_prod_obj.action_cancel(cr, uid, [mo.id], context=context)
        return super(SaleOrder, self).action_cancel(cr, uid, ids, context=context)

