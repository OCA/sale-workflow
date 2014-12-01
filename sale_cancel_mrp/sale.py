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
        mrp_prod_obj = self.pool.get('mrp.production')
        mo_ids = mrp_prod_obj.search(
            cr, uid, [('sale_order_id', 'in', ids)], context=context
        )
        cancel_ids = []
        for order in self.browse(cr, uid, ids, context=context):
            cancel = True
            for mo in mrp_prod_obj.browse(cr, uid, mo_ids, context=context):
                if mo.picking_id.state in ['assigned', 'confirmed', 'draft']:
                    mo.picking_id.action_cancel()
                    log = _("Canceled int picking on MO %s: %s")
                else:
                    cancel = False
                    log = _("Can't cancel int picking on MO %s: %s")
                log %= (mo.name, mo.picking_id.name)
                order.add_logs(log, cancel)
                if mo.state in ['draft', 'confirmed', 'ready']:
                    mo.action_cancel()
                    log = _("MO %s canceled")
                else:
                    cancel = False
                    log = _("Can't cancel MO: %s")
                log %= mo.name
                order.add_logs(log, cancel)
            if cancel:
                cancel_ids.append(order.id)
        return super(SaleOrder, self).action_cancel(
            cr, uid, cancel_ids, context=context
        )
