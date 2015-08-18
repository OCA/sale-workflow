# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution.
#    Copyright (C) 2014 OpusVL (<http://opusvl.com>).
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


class Common(object):
    @api.depends('origin')
    @api.one
    def _compute_client_order_ref(self):
        res = self._get_source_order()
        if res:
            order = res['order']
            self.source_doc_client_order_ref = (
                order.client_order_ref if res['model'] == 'sale.order'
                else order.source_doc_client_order_ref
            )

    def _get_source_order(self):
        if self.origin:
            matched_sale = self.env['sale.order'].search(
                [('name', '=', self.origin)]
            )
            matched_product = self.env['purchase.order'].search(
                [('name', '=', self.origin)]
            )
            if matched_sale:
                return {'order': matched_sale, 'model': 'sale.order'}
            elif matched_product:
                return {'order': matched_product, 'model': 'purchase.order'}
            else:
                return False
        else:
            return False


class source_doc_purchase_order(models.Model, Common):
    _inherit = "purchase.order"

    source_doc_client_order_ref = fields.Char(
        string='Order Reference(s)',
        compute='_compute_client_order_ref'
    )


class source_doc_stock_picking(models.Model, Common):
    _inherit = 'stock.picking'

    source_doc_client_order_ref = fields.Char(
        string='Order Reference',
        compute='_compute_client_order_ref',
        store=True,
    )
