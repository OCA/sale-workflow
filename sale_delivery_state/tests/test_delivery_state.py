# Copyright 2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestDeliveryState(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order = cls.env.ref("sale_delivery_state.sale_order_1")
        cls.delivery_cost = cls.env["product.product"].create(
            {"name": "delivery", "type": "service"}
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

    def mock_delivery(self):
        class DeliverySaleOrderLine(self.order.order_line._model_classes[0]):
            def _is_delivery(self):
                return True

        for line in self.order.order_line:
            if line.product_id == self.delivery_cost:
                line.__class__ = DeliverySaleOrderLine

    def add_delivery_cost_line(self):
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

    def test_no_delivery_delivery_cost(self):
        self.add_delivery_cost_line()
        self.mock_delivery()
        self.assertEqual(self.order.delivery_state, "no")

    def test_unprocessed_delivery_delivery_cost(self):
        self.add_delivery_cost_line()
        self.mock_delivery()
        self.order.action_confirm()
        self.assertEqual(self.order.delivery_state, "unprocessed")

    def test_partially_delivery_cost(self):
        self.add_delivery_cost_line()
        self.mock_delivery()
        self.order.action_confirm()
        self.order.order_line[0].qty_delivered = 2
        self.assertEqual(self.order.delivery_state, "partially")

    def test_forced_delivery_cost(self):
        self.add_delivery_cost_line()
        self.mock_delivery()
        self.order.action_confirm()
        self.order.order_line[0].qty_delivered = 2
        self.order.force_delivery_state = True
        self.assertEqual(self.order.delivery_state, "done")

    def test_delivery_done_delivery_cost(self):
        self.add_delivery_cost_line()
        self.mock_delivery()
        self.order.action_confirm()
        for line in self.order.order_line:
            if line._is_delivery():
                continue
            line.qty_delivered = line.product_uom_qty
        self.assertEqual(self.order.delivery_state, "done")
