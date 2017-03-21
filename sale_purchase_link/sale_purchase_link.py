# -*- coding: utf-8 -*-
##############################################################################
#
#  License AGPL version 3 or later
#  See license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields


class ProcurementOrder(orm.Model):
    _inherit = 'procurement.order'

    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals,
                                          line_vals, context=None):
        if procurement.move_id and procurement.move_id.sale_line_id:
            line_vals.update(
                {'sale_order_id': procurement.move_id.sale_line_id.order_id.id}
            )
        return super(ProcurementOrder, self).create_procurement_purchase_order(
            cr, uid, procurement, po_vals, line_vals, context=context)


class PurchaseOrderLine(orm.Model):
    _inherit = 'purchase.order.line'
    _columns = {
        'sale_order_id': fields.many2one('sale.order', 'Source Sale Order'),
    }


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def action_view_purchase_order(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        po_line_obj = self.pool.get('purchase.order.line')

        result = mod_obj.get_object_reference(
            cr, uid, 'purchase', 'purchase_form_action'
        )
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        line_ids = po_line_obj.search(
            cr, uid, [('sale_order_id', 'in', ids)], context=context
        )
        po_ids = []
        for line in po_line_obj.browse(cr, uid, line_ids, context=context):
            po_ids.append(line.order_id.id)
        result['domain'] = "[('id', 'in', %s)]" % po_ids
        return result
