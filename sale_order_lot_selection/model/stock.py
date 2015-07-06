# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for Odoo
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.ArithmeticError#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.ArithmeticError#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see
#   <http://www.gnu.org/licenses/>.ArithmeticError#
###############################################################################

from openerp import fields, api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _prepare_procurement_from_move(self, move):
        vals = super(StockMove, self)._prepare_procurement_from_move(move)
        vals['lot_id'] = move.restrict_lot_id.id
        return vals
