# Copyright 2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from unittest import mock

from dateutil.relativedelta import relativedelta

from odoo import Command
from odoo.tests.common import TransactionCase


class TestDeliveryState(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.order = cls.create_sale_order(cls)
        cls.delivery_cost = cls.env["product.product"].create(
            {"name": "delivery", "type": "service"}
        )
        cls.service_product = cls.env["product.product"].create(
            {"name": "service", "type": "service"}
        )

    def create_sale_order(self):
        # --- PARTNER ---
        partner_demo = self.env["res.partner"].create(
            {
                "name": "Demo Customer 2",
                "email": "demo.customer2@example.com",
            }
        )

        # --- USER DEMO ---
        user_demo = self.env["res.users"].create(
            {
                "name": "Demo User",
                "login": "demo_user",
                "email": "demo.user@example.com",
                "password": "demo_password",
            }
        )

        # --- UTM SOURCE ---
        utm_source = self.env["utm.source"].create(
            {
                "name": "Demo Source for Sale Order",
            }
        )

        # --- PRODUCTS ---
        product_25 = self.env["product.product"].create(
            {
                "name": "Product 25",
                "list_price": 295,
                "standard_price": 200,
                "type": "consu",
            }
        )

        product_delivery_02 = self.env["product.product"].create(
            {
                "name": "Delivery Product 02",
                "list_price": 145,
                "standard_price": 100,
                "type": "consu",
            }
        )

        product_delivery_01 = self.env["product.product"].create(
            {
                "name": "Delivery Product 01",
                "list_price": 65,
                "standard_price": 40,
                "type": "consu",
            }
        )
        utm_campaign_email_campaign_products = self.env["utm.campaign"].create(
            {
                "name": "Email Campaign - Products",
                "stage_id": self.env.ref("utm.default_utm_stage").id,
                "is_auto_campaign": True,
            }
        )

        # --- SALE ORDER ---
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": partner_demo.id,
                "partner_invoice_id": partner_demo.id,
                "partner_shipping_id": partner_demo.id,
                "user_id": user_demo.id,
                "team_id": self.env.ref("sales_team.team_sales_department").id,
                "campaign_id": utm_campaign_email_campaign_products.id,
                "medium_id": self.env.ref("utm.utm_medium_email").id,
                "source_id": utm_source.id,
                "date_order": (datetime.today() - relativedelta(months=1)).strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "order_line": [
                    Command.create(
                        {
                            "product_id": product_25.id,
                            "product_uom_qty": 3,
                            "price_unit": 295.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": product_delivery_02.id,
                            "product_uom_qty": 5,
                            "price_unit": 145.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": product_delivery_01.id,
                            "product_uom_qty": 2,
                            "price_unit": 65.0,
                        }
                    ),
                ],
            }
        )
        return sale_order

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
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
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
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "price_unit": 10.0,
                "skip_sale_delivery_state": skip_sale_delivery_state,
            }
        )

    def test_no_delivery(self):
        self.assertFalse(self.order.delivery_status)

    def test_unprocessed_delivery(self):
        self.order.action_confirm()
        self.assertEqual(self.order.delivery_status, "pending")

    def test_partially(self):
        self.order.action_confirm()
        self.order.order_line[0].qty_delivered = 2
        self.assertEqual(self.order.delivery_status, "partial")

    def test_delivery_done(self):
        self.order.action_confirm()
        for line in self.order.order_line:
            line.qty_delivered = line.product_uom_qty
        self.assertEqual(self.order.delivery_status, "full")

    def test_no_delivery_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.assertFalse(self.order.delivery_status)

    def test_unprocessed_delivery_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.order.action_confirm()
            self.assertEqual(self.order.delivery_status, "pending")

    def test_partially_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.order.action_confirm()
            self.order.order_line[0].qty_delivered = 2
            self.assertEqual(self.order.delivery_status, "partial")

    def test_forced_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.order.action_confirm()
            self.order.order_line[0].qty_delivered = 2
            self.order.force_delivery_state = True
            self.assertEqual(self.order.delivery_status, "full")

    def test_delivery_done_delivery_cost(self):
        self._add_delivery_cost_line()
        with self._mock_delivery():
            self.order.action_confirm()
            for line in self.order.order_line:
                if line._is_delivery():
                    continue
                line.qty_delivered = line.product_uom_qty
            self.assertEqual(self.order.delivery_status, "full")

    def test_skip_service_line(self):
        self._add_service_line()
        self.order.action_confirm()
        for line in self.order.order_line:
            if line.product_id == self.service_product:
                continue
            line.qty_delivered = line.product_uom_qty
        self.assertEqual(self.order.delivery_status, "partial")
        self.order.order_line.filtered(
            lambda a: a.product_id and a.product_id == self.service_product
        ).write({"skip_sale_delivery_state": True})
        self.assertEqual(self.order.delivery_status, "full")
