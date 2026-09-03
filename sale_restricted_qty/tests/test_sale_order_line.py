# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderLine(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Partner = cls.env["res.partner"]
        cls.Product = cls.env["product.product"]
        cls.ProductTemplate = cls.env["product.template"]
        cls.ProductCategory = cls.env["product.category"]
        cls.SaleOrder = cls.env["sale.order"]
        cls.Uom = cls.env["uom.uom"]

        cls.partner = cls.Partner.create({"name": "Partner"})
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")

    def test_min_qty_blocking_vs_warning(self):
        """Test the difference between Blocking and Warning for Min Qty."""
        product = self.Product.create(
            {
                "name": "Product",
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": "1",  # Blocking
            }
        )

        # 1. Blocking: Should raise ValidationError
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

        # 2. Warning: Should NOT raise ValidationError
        product.sale_restrict_min_qty = "0"  # Warning
        so = self.SaleOrder.create(
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
        self.assertTrue(so.order_line.is_below_min_qty)

    def test_max_qty_blocking_vs_warning(self):
        """Test the difference between Blocking and Warning for Max Qty."""
        product = self.Product.create(
            {
                "name": "Product",
                "sale_max_qty": 10.0,
                "sale_restrict_max_qty": "1",  # Blocking
            }
        )

        # 1. Blocking
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

        # 2. Warning
        product.sale_restrict_max_qty = "0"
        so = self.SaleOrder.create(
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
        self.assertTrue(so.order_line.is_above_max_qty)

    def test_multiple_of_qty_blocking_vs_warning(self):
        """Test the difference between Blocking and Warning for Multiple-of."""
        product = self.Product.create(
            {
                "name": "Product",
                "sale_multiple_of_qty": 5.0,
                "sale_restrict_multiple_of_qty": "1",  # Blocking
            }
        )

        # 1. Blocking
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
                                "product_uom_qty": 7.0,
                            },
                        )
                    ],
                }
            )

        # 2. Warning
        product.sale_restrict_multiple_of_qty = "0"
        so = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 7.0,
                        },
                    )
                ],
            }
        )
        self.assertTrue(so.order_line.is_not_multiple_of_qty)

    def test_multi_level_inheritance(self):
        """Test inheritance from Category -> Template -> Product."""
        parent_categ = self.ProductCategory.create(
            {
                "name": "Parent Categ",
                "sale_min_qty": 100.0,
                "sale_restrict_min_qty": "1",
            }
        )
        child_categ = self.ProductCategory.create(
            {
                "name": "Child Categ",
                "parent_id": parent_categ.id,
            }
        )
        template = self.ProductTemplate.create(
            {
                "name": "Template",
                "categ_id": child_categ.id,
            }
        )
        product = template.product_variant_id

        # Verify initial inheritance
        self.assertEqual(product.sale_min_qty, 100.0)
        self.assertEqual(product.sale_restrict_min_qty, "1")

        # Override at Template level
        template.sale_min_qty = 50.0
        self.assertEqual(product.sale_min_qty, 50.0)

        # Setting Template level back to inherited should restore category value
        template.is_sale_own_min_qty_set = False
        self.assertEqual(template.sale_min_qty, 100.0)
        self.assertEqual(product.sale_min_qty, 100.0)

    def test_auto_populate_logic(self):
        """Exhaustive test of auto-population onchanges."""
        product = self.Product.create(
            {
                "name": "Product",
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": "1",
            }
        )

        line = self.env["sale.order.line"].new(
            {
                "product_id": product.id,
            }
        )
        # Simulate UI trigger
        line._onchange_product_id()
        line._onchange_product_id_set_min_qty()
        self.assertEqual(line.product_uom_qty, 10.0)

        # Test that it DOES NOT overwrite if quantity is already set manually
        line.product_uom_qty = 25.0
        line._onchange_product_id_set_min_qty()
        self.assertEqual(line.product_uom_qty, 25.0)

    def test_uom_logic(self):
        """Test that constraints handle UoM conversions correctly."""
        product = self.Product.create(
            {
                "name": "Product",
                "uom_id": self.uom_unit.id,
                "sale_min_qty": 24.0,  # 2 Dozen
                "sale_restrict_min_qty": "1",
            }
        )

        # 1.5 Dozen = 18 Units (Fails)
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
                                "product_uom_qty": 1.5,
                                "product_uom_id": self.uom_dozen.id,
                            },
                        )
                    ],
                }
            )

        # 2.5 Dozen = 30 Units (Success)
        so = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 2.5,
                            "product_uom_id": self.uom_dozen.id,
                        },
                    )
                ],
            }
        )
        self.assertFalse(so.order_line.is_below_min_qty)

    def test_inverses_and_onchanges_mixin(self):
        """Test all logic branches in the mixin manually."""
        product = self.Product.create({"name": "Product"})

        # Test sale_min_qty inverse
        product.sale_min_qty = 12.3
        self.assertTrue(product.is_sale_own_min_qty_set)
        self.assertEqual(product.sale_own_min_qty, 12.3)

        # Reset via is_sale_own_min_qty_set
        product.is_sale_own_min_qty_set = False
        product._onchange_is_sale_min_qty_set()
        self.assertEqual(product.sale_min_qty, 0.0)

        # Test restriction selection inverse
        product.sale_restrict_min_qty = "1"
        self.assertTrue(product.is_sale_own_restrict_min_qty_set)
        self.assertEqual(product.sale_own_restrict_min_qty, "1")

    def test_historical_skip(self):
        """Ensure confirmed orders skip constraints."""
        product = self.Product.create({"name": "Product"})
        so = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1.0,
                        },
                    )
                ],
            }
        )
        so.action_confirm()

        # Enable restriction after confirmation
        product.write(
            {
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": "1",
            }
        )
        # This shouldn't crash or fail validation on re-read/write
        so.name = "Updated SO"
        self.assertEqual(so.order_line.product_uom_qty, 1.0)
