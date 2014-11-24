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
        for order in self.browse(cr, uid, ids, context=context):
            pickings = order.picking_ids
            for picking in pickings:
                if picking.state in ['assigned', 'confirmed', 'draft']:
                    picking.action_cancel()
                    log = "<p>Canceled picking out: %s</p>" % picking.name
                else:
                    log = "<p>Can't cancel picking out: %s</p>" % \
                        picking.name
                order.add_logs(log)
        return super(SaleOrder, self).action_cancel(
            cr, uid, ids, context=context
        )

    def add_logs(self, cr, uid, ids, log_message, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if order.cancel_logs:
                logs = order.cancel_logs
            else:
                logs = ""
            logs += '%s\n' % log_message
            self.write(
                cr, uid, [order.id], {'cancel_logs': logs}, context=context
            )

    _columns = {
        'cancel_logs': fields.html("Cancellation Logs"),
    }
