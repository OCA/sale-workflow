# -*- coding: utf-8 -*-

##############################################################################
#
# Delivery Notes
# Copyright (C) 2015 OpusVL (<http://opusvl.com/>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    split_to_moves = fields.One2many(
        comodel_name='stock.move',
        inverse_name='split_from',
    )

    outstanding_qty = fields.Float(
        compute='_outstanding_qty_compute',
        string='Outstanding',
    )

    @api.depends('split_to_moves.product_qty')
    def _outstanding_qty_compute(self):
        self.outstanding_qty = sum(self.split_to_moves.mapped('product_qty'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
