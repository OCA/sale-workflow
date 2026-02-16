# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleForecastAvailable(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
            }
        )
        cls.product_available = cls.env["product.product"].create(
            {
                "name": "Available Product",
                "type": "consu",
                "is_storable": True,
                "list_price": 100.0,
            }
        )
        cls.product_unavailable = cls.env["product.product"].create(
            {
                "name": "Unavailable Product",
                "type": "consu",
                "is_storable": True,
                "list_price": 100.0,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_available, cls.env.ref("stock.stock_location_stock"), 100.0
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")

    def test_01_order_with_available_stock(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_available.id,
                            "product_uom_qty": 10.0,
                        },
                    )
                ],
            }
        )
        self.assertFalse(
            order.order_line.forecasted_issue,
            "Line should have no forecast issue when stock is available",
        )
        self.assertTrue(
            order.sale_forecast_available,
            "Order should be forecast available when all lines have stock",
        )

    def test_02_order_with_mixed_lines(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_available.id,
                            "product_uom_qty": 10.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_unavailable.id,
                            "product_uom_qty": 50.0,
                        },
                    ),
                ],
            }
        )
        self.assertFalse(
            order.order_line[0].forecasted_issue, "First line should have no issues"
        )
        self.assertTrue(
            order.order_line[1].forecasted_issue,
            "Second line should have forecast issue",
        )
        self.assertFalse(
            order.sale_forecast_available,
            "Order should not be available if ANY line has issues",
        )

    def test_04_mto_product_no_issue(self):
        mto_route = self.env.ref("stock.route_warehouse0_mto")
        buy_route = self.env["stock.route"].search([("name", "=", "Buy")])
        mto_route.active = True
        mto_product = self.env["product.product"].create(
            {
                "name": "I AM MTO",
                "is_storable": True,
                "route_ids": [Command.set([buy_route.id, mto_route.id])],
                "company_id": False,
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": self.partner.id,
                            "min_qty": 1,
                            "price": 250,
                        }
                    ),
                ],
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": mto_product.id,
                            "product_uom_qty": 100.0,
                        },
                    )
                ],
            }
        )
        order.order_line._compute_forecasted_issue()
        order._compute_sale_forecast_available()
        self.assertFalse(
            order.order_line.forecasted_issue,
            "MTO products should not trigger forecast issues in draft/sent state",
        )
        self.assertTrue(
            order.sale_forecast_available,
            "Order with MTO product should be available in draft state",
        )
