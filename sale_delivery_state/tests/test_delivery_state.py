# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from mock import Mock
from functools import partial
from odoo.tests.common import TransactionCase


class TestDeliveryState(TransactionCase):

    def setUp(self):
        super(TestDeliveryState, self).setUp()
        self.order = self.env.ref('sale_delivery_state.sale_order_1')

    def test_no_delivery(self):
        self.assertEqual(self.order.delivery_state, 'no')

    def test_unprocessed_delivery(self):
        self.order.action_confirm()
        self.assertEqual(self.order.delivery_state, 'unprocessed')

    def test_partially(self):
        self.order.action_confirm()
        self.order.order_line[0].qty_delivered = 2
        self.assertEqual(self.order.delivery_state, 'partially')

    def test_delivery_done(self):
        self.order.action_confirm()
        for line in self.order.order_line:
            line.qty_delivered = line.product_uom_qty
        self.assertEqual(self.order.delivery_state, 'done')

    def mock_delivery(self):
        """
        Mock `delivery.carrier` model to make tests even if
        `delivery` module is not installed

        Warning this messes with create, makes sure you
        don't use create afterwards.
        """
        carrier_mock = Mock()

        def search_count(cost_id, domain, *args, **kwargs):
            """
            Mock search count for delivery.carrier
            as we want to make the tests even if `delivery`
            module is not installed
            """
            if domain[0][2] == cost_id:
                return 1
            return 0

        cost_id = self.env.ref('product.service_delivery').id
        carrier_mock._browse.return_value.search_count = partial(
            search_count, cost_id)
        self.env.registry['delivery.carrier'] = carrier_mock

    def add_delivery_cost_line(self):
        # let's assume for this test that service_delivery is assigned
        # to a carrier
        delivery_cost = self.env.ref('product.service_delivery')
        self.env['sale.order.line'].create({
            'order_id': self.order.id,
            'name': 'Delivery cost',
            'product_id': delivery_cost.id,
            'product_uom_qty': 1,
            'product_uom': self.env.ref('product.product_uom_unit').id,
            'price_unit': 10.0,
        })

    def test_no_delivery_delivery_cost(self):
        self.add_delivery_cost_line()
        self.mock_delivery()
        self.assertEqual(self.order.delivery_state, 'no')

    def test_unprocessed_delivery_delivery_cost(self):
        self.add_delivery_cost_line()
        self.mock_delivery()
        self.order.action_confirm()
        self.assertEqual(self.order.delivery_state, 'unprocessed')

    def test_partially_delivery_cost(self):
        self.add_delivery_cost_line()
        self.mock_delivery()
        self.order.action_confirm()
        self.order.order_line[0].qty_delivered = 2
        self.assertEqual(self.order.delivery_state, 'partially')

    def test_delivery_done_delivery_cost(self):
        self.add_delivery_cost_line()
        self.mock_delivery()
        self.order.action_confirm()
        delivery_cost = self.env.ref('product.service_delivery')
        for line in self.order.order_line:
            if line.product_id == delivery_cost:
                continue
            line.qty_delivered = line.product_uom_qty
        self.assertEqual(self.order.delivery_state, 'done')
