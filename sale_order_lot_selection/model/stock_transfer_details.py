# -*- coding: utf-8 -*-
#########################################################################
#                                                                       #
# Copyright (C) 2015  Agile Business Group                              #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU Affero General Public License as        #
# published by the Free Software Foundation, either version 3 of the    #
# License, or (at your option) any later version.                       #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
# GNU Affero General Public Licensefor more details.                    #
#                                                                       #
# You should have received a copy of the                                #
# GNU Affero General Public License                                     #
# along with this program.  If not, see <http://www.gnu.org/licenses/>. #
#                                                                       #
#########################################################################

from openerp import models


class stock_transfer_details(models.TransientModel):
    _inherit = 'stock.transfer_details'

    def default_get(self, cr, uid, fields, context=None):
        res = super(stock_transfer_details, self).default_get(
            cr, uid, fields, context=context)
        packop_obj = self.pool.get("stock.pack.operation")
        for item in res['item_ids']:
            packop = packop_obj.browse(
                cr, uid, item['packop_id'], context=context)
            if not item['lot_id']:
                if packop and len(packop.linked_move_operation_ids) == 1 and (
                    packop.linked_move_operation_ids.move_id.procurement_id and
                    packop.linked_move_operation_ids.move_id.procurement_id.
                        lot_id):
                    item['lot_id'] = (
                        packop.linked_move_operation_ids.
                        move_id.procurement_id.lot_id.id)
                else:
                    item['lot_id'] = False
        for pack in res['packop_ids']:
            packop = packop_obj.browse(
                cr, uid, pack['packop_id'], context=context)
            if not pack['lot_id']:
                if packop and len(packop.linked_move_operation_ids) == 1 and (
                    packop.linked_move_operation_ids.move_id.procurement_id and
                    packop.linked_move_operation_ids.move_id.procurement_id.
                        lot_id):
                    pack['lot_id'] = (
                        packop.linked_move_operation_ids.
                        move_id.procurement_id.lot_id.id)
                else:
                    pack['lot_id'] = False
        return res
