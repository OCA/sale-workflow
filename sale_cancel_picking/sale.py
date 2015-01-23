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


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'cancel_log': fields.html("Cancellation Logs"),
    }

    def _cancel_linked_record(self, cr, uid, order, context=None):
        """
        Method that cancels the pickings related to the order. It writes
        messages on the cancellation logs attribute.
        """
        for picking in order.picking_ids:
            able_to_cancel, message, important = \
                picking.can_cancel_picking_out()
            if able_to_cancel:
                picking.action_cancel()
            order.add_cancel_log(message, important=important)

    def action_cancel(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            self._cancel_linked_record(cr, uid, order, context=None)
        return super(SaleOrder, self).action_cancel(
            cr, uid, ids, context=context)

    def add_cancel_log(self, cr, uid, ids, message, important=False,
                       context=None):
        """
        Writes message on cancellation logs attribute of the sale order.
        If important (boolean) is True, the method will write it in red.
        """
        if not message:
            return True
        for order in self.browse(cr, uid, ids, context=context):
            log = order.cancel_log or ""
            if important:
                log += '<p style="color: red">%s</p>'
            else:
                log += '<p>%s</p>'
            order.write({'cancel_log': log % message})
        return True

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['cancel_log'] = False
        return super(SaleOrder, self).copy_data(
            cr, uid, id, default, context=context)
