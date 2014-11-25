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


class MrpProd(orm.Model):
    _inherit = 'mrp.production'

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        if 'move_prod_id' in vals:
            move = move_obj.browse(
                cr, uid, vals['move_prod_id'], context=context
            )
            if move.picking_id.sale_id:
                vals['sale_order_id'] = move.picking_id.sale_id.id
        return super(MrpProd, self).create(
            cr, uid, vals, context=context
        )

    _columns = {
        'sale_order_id': fields.many2one('sale.order', 'Source Sale Order'),
    }
