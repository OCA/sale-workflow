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

class ProcurementOrder(orm.Model):
    _inherit = 'procurement.order'

    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals,
                                            line_vals, context=None):
        if procurement.origin:
            sale_order_obj = self.pool.get('sale.order')
            sale_order_ids = sale_order_obj.search(
                cr, uid, [('name','=',procurement.origin)]
            )
            if len(sale_order_ids) == 1:
                line_vals.update({'sale_order_id':sale_order_ids[0]})
        return super(ProcurementOrder, self).create_procurement_purchase_order(
            cr, uid, procurement, po_vals, line_vals, context=context)

class PurchaseOrderLine(orm.Model):
    _inherit = 'purchase.order.line'
    _columns = {
        'sale_order_id': fields.many2one('sale.order', 'Source Sale Order'),
    }
