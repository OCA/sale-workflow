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

from openerp import fields, models, api


class procurement_order(models.Model):
    _inherit = 'procurement.order'

    lot_id = fields.Many2one('stock.production.lot', 'Lot')

    @api.model
    def _run(self, procurement):
        res = super(
            procurement_order, self)._run(procurement)
        for move in procurement.move_ids:
            move.action_assign()
        return res

    @api.model
    def _run_move_create(self, procurement):
        res = super(
            procurement_order, self)._run_move_create(procurement)
        res['restrict_lot_id'] = procurement.lot_id.id
        return res
