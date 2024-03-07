# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.exceptions import ValidationError


class TestSaleOrderLine(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Partner = cls.env["res.partner"]
        cls.Product = cls.env["product.product"]
        cls.SaleOrder = cls.env["sale.order"]

        cls.partner = cls.Partner.create({"name": "Partner"})

    def test_min_qty(self):
        product = self.Product.create(
            {
                "name": "Product",
                "sale_min_qty": 10.0,
            }
        )
        self.assertTrue(product.is_sale_own_min_qty_set)
        self.assertEqual(product.sale_own_min_qty, 10.0)

        sale_order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 5.0,
                        },
                    )
                ],
            }
        )
        self.assertEqual(sale_order.order_line.min_qty, 10.0)
        self.assertFalse(sale_order.order_line.restrict_min_qty)
        self.assertTrue(sale_order.order_line.is_below_min_qty)

    def test_min_qty_restricted(self):
        product = self.Product.create(
            {
                "name": "Product",
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": "1",
            }
        )
        self.assertTrue(product.is_sale_own_min_qty_set)
        self.assertEqual(product.sale_own_min_qty, 10.0)
        self.assertTrue(product.is_sale_own_restrict_min_qty_set)
        self.assertEqual(product.sale_own_restrict_min_qty, "1")

        with self.assertRaises(ValidationError):
            self.SaleOrder.create(
                {
                    "partner_id": self.partner.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": product.id,
                                "product_uom_qty": 5.0,
                            },
                        )
                    ],
                }
            )

    def test_max_qty(self):
        product = self.Product.create(
            {
                "name": "Product",
                "sale_max_qty": 10.0,
            }
        )
        self.assertTrue(product.is_sale_own_max_qty_set)
        self.assertEqual(product.sale_own_max_qty, 10.0)

        sale_order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 15.0,
                        },
                    )
                ],
            }
        )
        self.assertEqual(sale_order.order_line.max_qty, 10.0)
        self.assertFalse(sale_order.order_line.restrict_max_qty)
        self.assertTrue(sale_order.order_line.is_above_max_qty)

    def test_max_qty_restricted(self):
        product = self.Product.create(
            {
                "name": "Product",
                "sale_max_qty": 10.0,
                "sale_restrict_max_qty": "1",
            }
        )
        self.assertTrue(product.is_sale_own_max_qty_set)
        self.assertEqual(product.sale_own_max_qty, 10.0)
        self.assertTrue(product.is_sale_own_restrict_max_qty_set)
        self.assertEqual(product.sale_own_restrict_max_qty, "1")

        with self.assertRaises(ValidationError):
            self.SaleOrder.create(
                {
                    "partner_id": self.partner.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": product.id,
                                "product_uom_qty": 15.0,
                            },
                        )
                    ],
                }
            )
