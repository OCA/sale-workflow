# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
import openerp.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    standard_price = fields.Float(
        related='product_id.standard_price',
        string='Cost Price',
        digits_compute=dp.get_precision('Product Price'),
    )

    @api.one
    @api.depends('product_id')
    def compute_qty_available(self):
        """Get the quantity available in the selected warehouse"""
        order = self.order_id
        self.qty_available = sum(
            quant.qty for quant in
            self.env['stock.quant'].search([
                ('location_id', '=', order.warehouse_id.
                    lot_stock_id.id),
                ('product_id', '=', self.product_id.id),
                '|',
                ('reservation_id.group_id.name', 'in',
                    [False, order.name]),
                ('reservation_id', '=', False),
            ])
        )

    @api.one
    @api.depends('qty_available', 'product_uom_qty')
    def compute_is_available(self):
        """Define whether the line will be displayed in red or not"""
        self.is_available = self.order_id.shipped or \
            not self.product_id or self.product_id.type != 'product' or \
            self.qty_available - self.product_uom_qty >= 0

    qty_available = fields.Float(
        string='Available Quantity',
        digits_compute=dp.get_precision('Product UoS'),
        compute='compute_qty_available',
        readonly=True,
        store=False,
    )

    is_available = fields.Boolean(
        string='Product Available',
        compute='compute_is_available',
        help='whether the quantity in stock is sufficient',
        store=False,
    )
