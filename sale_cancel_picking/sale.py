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

    _columns = {
        'cancel_log': fields.html("Cancellation Logs"),
    }

    def _can_cancel_picking_out(self, cr, uid, picking, context=None):
        """
        Method that return if it's possible or not to cancel the picking_out
        By default we raise an error if the picking is done.
        You can override this behaviours if needed in your custom module

        :param order: Picking
        :type items: browse_record
        :return: tuple that contain the following value
            (able_to_cancel, message, important)
        """
        able_to_cancel = False
        important = False
        message = ""

        if picking.state == 'cancel':
            pass
        elif picking.state == 'done':
            raise orm.except_orm(
                _('User Error'),
                _('The Sale Order %s can not be cancelled as the picking'
                  ' %s is in the done state')
                % (picking.sale_id.name, picking.name))
        else:
            able_to_cancel = True
            message = _("Canceled picking out: %s") % picking.name
        return able_to_cancel, message, important

    def _cancel_linked_record(self, cr, uid, order, context=None):
        for picking in order.picking_ids:
            able_to_cancel, message, important = \
                self._can_cancel_picking_out(cr, uid, picking, context=context)
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
