#    Author: Leonardo Pistone
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
from openerp.tests.common import TransactionCase


class TestConsistentRoute(TransactionCase):
    def test_dropshipping_route_purchase_to_customer_passes(self):
        self.sale_line.route_id = self.dropship
        self.po.location_id.usage = 'customer'
        self.assertIs(True, self.sale_line.has_consistent_route())

    def test_dropshipping_route_purchase_to_internal_fails(self):
        self.sale_line.route_id = self.dropship
        self.po.location_id.usage = 'internal'
        self.assertIs(False, self.sale_line.has_consistent_route())

    def test_mto_route_purchase_to_customer_fails(self):
        self.sale_line.route_id = self.mto
        self.po.location_id.usage = 'customer'
        self.assertIs(False, self.sale_line.has_consistent_route())

    def test_mto_route_purchase_to_internal_passes(self):
        self.sale_line.route_id = self.mto
        self.po.location_id.usage = 'internal'
        self.assertIs(True, self.sale_line.has_consistent_route())

    def test_no_route_passes(self):
        self.assertIs(True, self.sale_line.has_consistent_route())

    def setUp(self):
        super(TestConsistentRoute, self).setUp()
        self.dropship = self.env.ref('stock_dropshipping.route_drop_shipping')
        self.mto = self.env.ref('stock.route_warehouse0_mto')
        self.po = self.env['purchase.order'].new({
            'location_id': self.env['stock.location'].new(),
        })
        self.purchase_line = self.env['purchase.order.line'].new({
            'order_id': self.po,
        })
        self.sale_line = self.env['sale.order.line'].new({
            'sourced_by': self.purchase_line,
        })
