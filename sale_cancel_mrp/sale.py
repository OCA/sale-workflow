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
            cr, uid, [('sale_order_id', 'in', ids)], context=context
        )
        for order in self.browse(cr, uid, ids, context=context):
            for mo in mrp_prod_obj.browse(cr, uid, mo_ids, context=context):
                if mo.picking_id.state in ['assigned', 'confirmed', 'draft'] \
                        and mo.state in ['draft', 'confirmed']:
                    mo.picking_id.action_cancel()
                    log = "<p>Canceled internal picking on MO %s: %s</p>" % \
                        (mo.name, mo.picking_id.name)
                else:
                    log = "<p>Can't cancel MO %s or internal picking %s on MO \
                        </p>" % (mo.name, mo.picking_id.name)
                order.add_logs(log)
                mo.action_cancel()
                order.add_logs("<p>MO %s canceled</p>" % mo.name)
        return super(SaleOrder, self).action_cancel(
            cr, uid, ids, context=context
        )
