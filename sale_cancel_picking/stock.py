# -*- coding: utf-8 -*-
##############################################################################
#
#  License AGPL version 3 or later
#  See license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class StockPickingOut(orm.Model):
    _inherit = 'stock.picking.out'

    def can_cancel_picking_out(self, cr, uid, ids, context=None):
        """
        Method that returns if it's possible or not to cancel the picking_out
        By default we raise an error if the picking is done.
        You can override this behaviours if needed in your custom module

        :param
        :type items: browse_record
        :return: tuple that contains the following value
            (able_to_cancel, message, important)
        """
        able_to_cancel = False
        important = False
        message = ""

        assert len(ids) == 1, 'This option should only be used for a single id'
        ' at a time'
        picking = self.browse(cr, uid, ids, context=context)[0]
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
