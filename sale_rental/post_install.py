# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale Rental module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import SUPERUSER_ID


def set_rental_route_on_warehouse(cr, pool):
    """This post_install script is required because, when the module
    is installed, Odoo creates the column in the DB and compute the field
    and THEN it loads the file data/res_country_department_data.yml...
    So, when it computes the field on module installation, the
    departments are not available in the DB, so the department_id field
    on res.partner stays null. This post_install script fixes this."""
    swo = pool['stock.warehouse']
    warehouse_ids = swo.search(cr, SUPERUSER_ID, [])
    rental_route_id = pool['ir.model.data'].xmlid_to_res_id(
        cr, SUPERUSER_ID, 'sale_rental.route_warehouse0_rental')
    sell_rented_route_id = pool['ir.model.data'].xmlid_to_res_id(
        cr, SUPERUSER_ID, 'sale_rental.route_warehouse0_sell_rented_product')
    swo.write(
        cr, SUPERUSER_ID, warehouse_ids, {
            'rental_route_id': rental_route_id,
            'sell_rented_product_route_id': sell_rented_route_id,
            })
    return
