# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Alexandre Fayolle
#    Copyright 2014-2015 Camptocamp SA
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

    def setUp(self):
        super(TestSourcedBy, self).setUp()
        self.warehouse = self.env.ref('stock.warehouse0')
        self.warehouse.write({'reception_steps': 'transit_three_steps',
                              'delivery_steps': 'pick_pack_ship_transit'})

    def test_get_po_usage_transit_in(self):
        so_line_model = self.env['sale.order.line']
        po = self.env.ref('purchase.purchase_order_2')
        po_line = po.order_line[0]
        po.write({'location_id': self.warehouse.wh_transit_in_loc_id.id})
        usage = so_line_model._get_po_location_usage(po_line)
        self.assertEqual(usage, 'internal')

    def test_get_po_usage_transit_out(self):
        so_line_model = self.env['sale.order.line']
        po = self.env.ref('purchase.purchase_order_2')
        po_line = po.order_line[0]
        po.write({'location_id': self.warehouse.wh_transit_out_loc_id.id})
        usage = so_line_model._get_po_location_usage(po_line)
        self.assertEqual(usage, 'customer')
