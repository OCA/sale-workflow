# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Camptocamp (<http://www.camptocamp.com>)
#    Authors: Joel Grand-Guillaume
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp import netsvc
import logging
_logger = logging.getLogger(__name__)

class sale_order(orm.Model):
    _inherit = "sale.order"

    def _create_pickings_and_procurements(self, cr, uid, order, order_lines,
                                          picking_id=False, context=None):
        """Override the method to launch the procurement automatically for
        all line with a service product.

        :param browse_record order: sales order to which the order lines belong
        :param list(browse_record) order_lines: sales order line records to procure
        :param int picking_id: optional ID of a stock picking to which
                               the created stock moves will be added.
                               A new picking will be created if ommitted.
        :return: True

        """
        res = super(sale_order, self)._create_pickings_and_procurements(
            cr,
            uid,
            order,
            order_lines,
            picking_id=picking_id,
            context=context
        )
        wf_service = netsvc.LocalService("workflow")
        order.refresh()
        for line in order.order_line:
            if line.product_id and line.product_id.type == 'service':
                if line.procurement_id:
                    _logger.debug('Trigger button check on procurement`%s`, id %s',
                                  line.procurement_id.name, line.id)
                    proc_id = line.procurement_id.id
                    wf_service.trg_validate(uid,
                                            'procurement.order',
                                            proc_id,
                                            'button_check',
                                            cr)
        return res
