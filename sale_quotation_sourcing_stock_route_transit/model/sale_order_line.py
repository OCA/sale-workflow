# -*- coding: utf-8 -*-
#
#    Author: Alexandre Fayolle, Leonardo Pistone
#    Copyright 2015 Camptocamp SA
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
from openerp import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def _get_po_location_usage(self, purchase_order_line):
        """in case the PO delivers to a transit stock.location, implement a correct
        usage computation.

        If there is a stock.warehouse with this location set as input transit
        location, then we consider this as 'internal'; else if there is a stock
        warehouse with this location set as output transit location, then we
        consider this as 'customer'.
        """
        _super = super(SaleOrderLine, self)
        usage = _super._get_po_location_usage(purchase_order_line)
        if usage == 'transit':
            StockWarehouse = self.env['stock.warehouse']
            location = purchase_order_line.order_id.location_id
            domain_input = [('wh_transit_in_loc_id', '=', location.id)]
            domain_output = [('wh_transit_out_loc_id', '=', location.id)]
            if StockWarehouse.search(domain_input, limit=1):
                usage = 'internal'
            elif StockWarehouse.search(domain_output, limit=1):
                usage = 'customer'
        return usage
