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

    def _can_cancel_mo_internal_move(self, cr, uid, mo, context=None):
        """
        Method that return if it's possible or not to cancel the internal
        move linked to the manufacturing order

        :param mo: Manufacturing Order
        :type items: browse_record
        :return: tuple that contain the following value
            (able_to_cancel, message, important)
        """
        able_to_cancel = False
        important = False
        message = ""

        if mo.picking_id.state == 'cancel':
            pass
        elif mo.picking_id.state != 'done':
            able_to_cancel = True
            message = _("Canceled the internal move %s for the MO %s") \
                % (mo.picking_id.name, mo.name)
        else:
            important = True
            message = _("Fail to cancel the internal move %s for the "
                        "MO %s as it's in the done state") \
                % (mo.picking_id.name, mo.name)
        return able_to_cancel, message, important

    def _can_cancel_mo(self, cr, uid, mo, context=None):
        """
        Method that return if it's possible or not to cancel the
        manufacturing order

        :param mo: Manufacturing Order
        :type items: browse_record
        :return: tuple that contain the following value
            (able_to_cancel, message, important)
        """
        able_to_cancel = False
        important = False
        message = ""

        if mo.state == 'cancel':
            pass
        if mo.state != 'done':
            able_to_cancel = True
            message = _("MO %s canceled")
        else:
            important = True
            message = _("Fail to cancel the Manufacturing Order %s as it's"
                        " already done" % mo.name)
        return able_to_cancel, message, important

    def _cancel_linked_record(self, cr, uid, order, context=None):
        mrp_prod_obj = self.pool.get('mrp.production')
        mo_ids = mrp_prod_obj.search(cr, uid, [
            ('sale_order_id', '=', order.id),
            ], context=context)
        for mo in mrp_prod_obj.browse(cr, uid, mo_ids, context=context):
            able_to_cancel, message, important =\
                self._can_cancel_mo_internal_move(cr, uid, mo, context=context)
            if able_to_cancel:
                mo.picking_id.action_cancel()
            order.add_cancel_log(message, important=important)

            able_to_cancel, message, important =\
                self._can_cancel_mo(cr, uid, mo, context=context)
            if able_to_cancel:
                mo.action_cancel()
            order.add_cancel_log(message, important=important)
        return super(SaleOrder, self)._cancel_linked_record(
            cr, uid, order, context=context)
