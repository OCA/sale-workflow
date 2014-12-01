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

    def _can_unlink_purchase_line(self, cr, uid, po_line, context=None):
        """
        Method that return if it's possible or not to unlink the purchase line

        :param order: Purchase Order Line
        :type items: browse_record
        :return: tuple that contain the following value
            (able_to_cancel, message, important)
        """
        able_to_unlink = False
        important = False
        message = ""

        if po_line.state == 'cancel':
            pass
        if po_line.state == 'draft':
            able_to_unlink = True
        else:
            able_to_unlink = False
            important = True
            message = _("Fail to cancel the line with the product %s "
                        " in the purchase order %s as the state is %s") \
                      % (po_line.product_id.name, po_line.order_id.name,
                      po_line.state)
        return able_to_unlink, message, important

    def _cancel_linked_record(self, cr, uid, order, context=None):
        po_line_obj = self.pool['purchase.order.line']
        po_line_ids = po_line_obj.search(cr, uid, [
            ('sale_order_id', '=', order.id),
            ], context=context)
        count = 0
        for po_line in po_line_obj.browse(cr, uid, po_line_ids,
                                          context=context):
            able_to_unlink, message, important = \
                self._can_unlink_purchase_line(
                    cr, uid, po_line, context=context)
            if able_to_unlink:
                count += 1
                po_line.unlink()

            order.add_cancel_log(message, important)
        if count:
            order.add_cancel_log(
                _("Number of purchase order lines deleted: %s")% count)
        return super(SaleOrder, self)._cancel_linked_record(
            cr, uid, order, context=context)
