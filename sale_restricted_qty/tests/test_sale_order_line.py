# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.exceptions import ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
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

    def test_auto_populate_min_qty(self):
        """Test that the quantity is auto-populated with minimum quantity when enforced."""
        product = self.Product.create(
            {
                "name": "Product",
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": "1",  # Enforced
            }
        )
        
        # Test the onchange behavior directly
        sale_order_line = self.env["sale.order.line"].new({
            "product_id": product.id,
        })
        
        # Trigger the product onchange - quantity should auto-populate to minimum
        sale_order_line._onchange_product_id()
        sale_order_line._onchange_product_id_set_min_qty()
        
        # Check that quantity was auto-populated to the minimum value
        self.assertEqual(sale_order_line.product_uom_qty, 10.0)
        self.assertEqual(sale_order_line.min_qty, 10.0)
        self.assertTrue(sale_order_line.restrict_min_qty)
        
    def test_no_auto_populate_when_not_enforced(self):
        """Test that quantity is not auto-populated when minimum quantity is not enforced."""
        product = self.Product.create(
            {
                "name": "Product",
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": "0",  # Not enforced
            }
        )
        
        # Create sale order line with zero quantity - should NOT auto-populate
        sale_order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 0.0,
                        },
                    )
                ],
            }
        )
        
        # Check that quantity was NOT auto-populated
        self.assertEqual(sale_order.order_line.product_uom_qty, 0.0)
        self.assertEqual(sale_order.order_line.min_qty, 10.0)
        self.assertFalse(sale_order.order_line.restrict_min_qty)
        
    def test_onchange_auto_populate_min_qty(self):
        """Test that onchange properly auto-populates minimum quantity."""
        product = self.Product.create(
            {
                "name": "Product",
                "sale_min_qty": 15.0,
                "sale_restrict_min_qty": "1",  # Enforced
            }
        )
        
        # Test the onchange behavior directly
        sale_order_line = self.env["sale.order.line"].new({
            "product_id": product.id,
        })
        
        # Trigger the product onchange - quantity should auto-populate to minimum
        sale_order_line._onchange_product_id()
        sale_order_line._onchange_product_id_set_min_qty()
        
        # Check that quantity was auto-populated to the minimum value
        self.assertEqual(sale_order_line.product_uom_qty, 15.0)
        self.assertEqual(sale_order_line.min_qty, 15.0)
        self.assertTrue(sale_order_line.restrict_min_qty)
        
    def test_no_auto_populate_when_not_enforced(self):
        """Test that quantity is not auto-populated when minimum quantity is not enforced."""
        product = self.Product.create(
            {
                "name": "Product",
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": "0",  # Not enforced
            }
        )
        
        # Test the onchange behavior
        sale_order_line = self.env["sale.order.line"].new({
            "product_id": product.id,
        })
        
        # Trigger the product onchange
        sale_order_line._onchange_product_id()
        sale_order_line._onchange_product_id_set_min_qty()
        
        # Check that quantity was NOT auto-populated (remains at default 1.0)
        self.assertEqual(sale_order_line.product_uom_qty, 1.0)
        self.assertEqual(sale_order_line.min_qty, 10.0)
        self.assertFalse(sale_order_line.restrict_min_qty)
