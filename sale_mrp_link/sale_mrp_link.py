# -*- coding: utf-8 -*-
##############################################################################
#
#  License AGPL version 3 or later
#  See license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from osv import orm, fields


class MrpProd(orm.Model):
    _inherit = 'mrp.production'

    def _get_sale_order(self, cr, uid, move, context=None):
        sale_id = None
        if move.picking_id.sale_id:
            sale_id = move.picking_id.sale_id.id
        return sale_id

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        if 'move_prod_id' in vals:
            move = move_obj.browse(
                cr, uid, vals['move_prod_id'], context=context)
            sale_id = self._get_sale_order(cr, uid, move, context=context)
            if sale_id:
                vals['sale_order_id'] = sale_id
        return super(MrpProd, self).create(
            cr, uid, vals, context=context)

    _columns = {
        'sale_order_id': fields.many2one('sale.order', 'Source Sale Order'),
    }


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def action_view_manufacturing_order(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        mrp_prod_obj = self.pool.get('mrp.production')

        result = mod_obj.get_object_reference(
            cr, uid, 'mrp', 'mrp_production_action'
        )
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        mo_ids = mrp_prod_obj.search(
            cr, uid, [('sale_order_id', 'in', ids)], context=context)
        result['domain'] = "[('id', 'in', [" + \
            ','.join(map(str, mo_ids)) + "])]"
        return result
