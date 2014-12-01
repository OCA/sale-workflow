# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def action_cancel(self, cr, uid, ids, context=None):
        cancel_ids = []
        for order in self.browse(cr, uid, ids, context=context):
            cancel = True
            for picking in order.picking_ids:
                if picking.state in ['assigned', 'confirmed', 'draft']:
                    picking.action_cancel()
                    log = _("Canceled picking out: %s")
                else:
                    cancel = False
                    log = _("Can't cancel picking out: %s")
                log %= picking.name
                order.add_logs(log, cancel)
            if cancel:
                cancel_ids.append(order.id)
        return super(SaleOrder, self).action_cancel(
            cr, uid, cancel_ids, context=context
        )

    def add_logs(self, cr, uid, ids, log_message, success, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if order.cancel_logs:
                logs = order.cancel_logs
            else:
                logs = ""
            if success:
                logs += '<p>%s</p>'
            else:
                logs += '<p style="color: red">%s</p>'
            order.write({'cancel_logs': logs % log_message})

    _columns = {
        'cancel_logs': fields.html("Cancellation Logs"),
    }
