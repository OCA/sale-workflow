# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock

from odoo.tests import SavepointCase


class TestSaleLineDeliveryState(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Base data
        partner = cls.env.ref("base.res_partner_2")
        product = cls.env.ref("product.product_product_25")
        pricelist = cls.env.ref("product.list0")
        cls.uom = cls.env.ref("uom.product_uom_unit")
        # Create delivery product
        cls.delivery_cost = cls.env["product.product"].create(
            {"name": "delivery", "type": "service"}
        )
        # Create sales order
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "pricelist_id": pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom": cls.uom.id,
                            "product_uom_qty": 3,
                            "price_unit": 2950.00,
                            "name": product.name,
                        },
                    )
                ],
            }
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
                "product_uom": self.uom.id,
                "price_unit": 10.0,
            }
        )

    def test_no_delivery(self):
        self.assertEqual(self.order.order_line[0].delivery_state, "no")

    def test_unprocessed_delivery(self):
        self.order.action_confirm()
        self.assertEqual(self.order.order_line[0].delivery_state, "unprocessed")

    def test_partially(self):
        self.order.action_confirm()
        self.order.order_line[0].qty_delivered = 2
        self.assertEqual(self.order.order_line[0].delivery_state, "partially")

    def test_delivery_done(self):
        self.order.action_confirm()
        self.order.order_line[0].qty_delivered = 3
        self.assertEqual(self.order.order_line[0].delivery_state, "done")

    def test_no_delivery_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.assertEqual(self.order.order_line[1].delivery_state, "no")

    def test_unprocessed_delivery_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.order.action_confirm()
            self.assertEqual(self.order.order_line[0].delivery_state, "unprocessed")
            self.assertEqual(self.order.order_line[1].delivery_state, "no")

    def test_partially_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.order.action_confirm()
            self.order.order_line[0].qty_delivered = 2
            self.assertEqual(self.order.order_line[0].delivery_state, "partially")
            self.assertEqual(self.order.order_line[1].delivery_state, "no")

    def test_forced_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.order.action_confirm()
            self.order.order_line[0].qty_delivered = 2
            self.order.order_line[0].force_delivery_state = True
            self.assertEqual(self.order.order_line[0].delivery_state, "done")
            self.assertEqual(self.order.order_line[1].delivery_state, "no")

    def test_delivery_done_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.order.action_confirm()
            self.order.order_line[0].qty_delivered = 3
            self.assertEqual(self.order.order_line[0].delivery_state, "done")
            self.assertEqual(self.order.order_line[1].delivery_state, "no")
