# -*- coding: utf-8 -*-
#
#
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
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
#

from openerp import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _prepare_invoice_line(
            self, group, picking, move_line, invoice_id, invoice_vals):
        res = super(stock_picking, self)._prepare_invoice_line(
            group, picking, move_line, invoice_id, invoice_vals)
        res['sequence'] = move_line.sequence
        return res
