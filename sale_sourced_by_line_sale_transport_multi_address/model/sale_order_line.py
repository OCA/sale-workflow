# -*- coding: utf-8 -*-
#    Author: Alexandre Fayolle
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
from openerp import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('order_id.warehouse_id.partner_id',
                 'route_id',
                 'order_id.company_id.partner_id',
                 'warehouse_id.partner_id')
    @api.one
    def _origin_address(self):
        super(SaleOrderLine, self)._origin_address()
        if self.warehouse_id.partner_id:
            address = self.warehouse_id.partner_id
            self.origin_address_id = address
