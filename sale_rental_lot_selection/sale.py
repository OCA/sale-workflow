# -*- coding: utf-8 -*-
##############################################################################
#
#    Sale Rental Lot Selection module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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


from openerp import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def _select_lot_product(self, product):
        if product.rented_product_id:
            return product.rented_product_id
        else:
            return super(SaleOrderLine, self)._select_lot_product(product)

    @api.model
    def _select_lot_stock_location(self, product, warehouse):
        if product.rented_product_id:
            return warehouse.rental_view_location_id
        else:
            return super(SaleOrderLine, self)._select_lot_stock_location(
                product, warehouse)


class SaleRental(models.Model):
    _inherit = 'sale.rental'

    lot_id = fields.Many2one(
        'stock.production.lot', related='start_order_line_id.lot_id',
        string='Lot/Serial Number', readonly=True)
