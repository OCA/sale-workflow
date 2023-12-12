# Copyright 2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock

from odoo.tests import SavepointCase


class TestDeliveryState(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.order = cls.env.ref("sale_delivery_state.sale_order_1")
        cls.delivery_cost = cls.env["product.product"].create(
            {"name": "delivery", "type": "service"}
        )
        cls.service_product = cls.env["product.product"].create(
            {"name": "service", "type": "service"}
        )

    def _mock_delivery(self, delivery_prod=None):
        delivery_prod = delivery_prod or self.delivery_cost
        return mock.patch.object(
            type(self.env["sale.order.line"]),
            "_is_delivery",
            lambda self: self.product_id == delivery_prod,
        )

    def _add_delivery_cost_line(self):
        self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "name": "Delivery cost",
                "product_id": self.delivery_cost.id,
                "product_uom_qty": 1,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "price_unit": 10.0,
            }
        )

    def _add_service_line(self, skip_sale_delivery_state=False):
        self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "name": "Service",
                "product_id": self.service_product.id,
                "product_uom_qty": 1,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "price_unit": 10.0,
                "skip_sale_delivery_state": skip_sale_delivery_state,
            }
        )

    def test_no_delivery(self):
        self.assertEqual(self.order.delivery_state, "no")

    def test_unprocessed_delivery(self):
        self.order.action_confirm()
        self.assertEqual(self.order.delivery_state, "unprocessed")

    def test_partially(self):
        self.order.action_confirm()
        self.order.order_line[0].qty_delivered = 2
        self.assertEqual(self.order.delivery_state, "partially")

    def test_delivery_done(self):
        self.order.action_confirm()
        for line in self.order.order_line:
            line.qty_delivered = line.product_uom_qty
        self.assertEqual(self.order.delivery_state, "done")

    def test_no_delivery_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.assertEqual(self.order.delivery_state, "no")

    def test_unprocessed_delivery_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.order.action_confirm()
            self.assertEqual(self.order.delivery_state, "unprocessed")

    def test_partially_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.order.action_confirm()
            self.order.order_line[0].qty_delivered = 2
            self.assertEqual(self.order.delivery_state, "partially")

    def test_forced_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.order.action_confirm()
            self.order.order_line[0].qty_delivered = 2
            self.order.force_delivery_state = True
            self.assertEqual(self.order.delivery_state, "done")

    def test_delivery_done_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.order.action_confirm()
            for line in self.order.order_line:
                if line._is_delivery():
                    continue
                line.qty_delivered = line.product_uom_qty
            self.assertEqual(self.order.delivery_state, "done")

    def test_skip_service_line(self):
        self._add_service_line()
        self.order.action_confirm()
        for line in self.order.order_line:
            if line.product_id == self.service_product:
                continue
            line.qty_delivered = line.product_uom_qty
        self.assertEqual(self.order.delivery_state, "partially")
        self.order.order_line.filtered(
            lambda a: a.product_id and a.product_id == self.service_product
        ).write({"skip_sale_delivery_state": True})
        self.assertEqual(self.order.delivery_state, "done")
