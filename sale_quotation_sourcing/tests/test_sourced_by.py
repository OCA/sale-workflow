# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2014 Camptocamp SA
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
import openerp.tests.common as test_common


class TestSourcedBy(test_common.TransactionCase):

    def test_get_route_from_usage(self):
        so_line_model = self.env['sale.order.line']
        ds_route = self.env.ref('stock_dropshipping.route_drop_shipping')
        mto_route = self.env.ref('stock.route_warehouse0_mto')
        self.assertTrue(ds_route)
        self.assertTrue(mto_route)
        self.assertEqual(
            so_line_model._find_route_from_usage('customer'),
            ds_route
        )
        self.assertEquals(
            so_line_model._find_route_from_usage('internal'),
            mto_route
        )
        self.assertEquals(
            so_line_model._find_route_from_usage('supplier'),
            None
        )

    def test_get_po_usage(self):
        so_line_model = self.env['sale.order.line']
        po_line = self.env.ref('purchase.purchase_order_2').order_line[0]
        usage = so_line_model._get_po_location_usage(po_line)
        self.assertEqual(usage, 'internal')
