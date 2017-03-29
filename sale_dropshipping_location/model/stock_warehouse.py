# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              Jordi Ballester Alomar <jordi.ballester@eficent.com>
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

from openerp.osv import fields, osv

class stock_warehouse(osv.osv):
    _inherit = "stock.warehouse"

    _columns = {
        'property_stock_drop_ship': fields.property(
            'stock.location',
            type='many2one',
            relation='stock.location',
            string="Drop Ship Location",
            view_load=True,
            help="This stock location will be used, "
                 "as the destination location for stock moves "
                 "related to direct shipments from vendor "
                 "to the customer."),

        'property_stock_drop_ship_return': fields.property(
            'stock.location',
            type='many2one',
            relation='stock.location',
            string="Drop Ship Returns Location",
            view_load=True,
            help="This stock location will be used, "
                 "as the destination location for stock moves "
                 "related to return direct shipments from customer "
                 "to the vendor."),
    }

