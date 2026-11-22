# Copyright 2025 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestQuantityRestriction(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # --- Used Models ---
        cls.Restriction = cls.env["sale.quantity.restriction"]
        cls.Category = cls.env["product.category"]
        cls.SaleOrderLine = cls.env["sale.order.line"]
        cls.Product = cls.env["product.product"]

        # --- Restriction Rules ---
        # 1. Category A Rule: Min 10 (Mandatory), Multiple 5 (Non-Mandatory)
        cls.rule_category_min = cls.Restriction.create(
            {
                "name": "Category Rule - Min 10",
                "min_qty": 10.0,
                "is_min_mandatory": True,
                "multiple_qty": 5.0,
                "is_multiple_mandatory": False,
            }
        )

        # 2. Manual Override Rule: Max 50 (Mandatory)
        cls.rule_override_max = cls.Restriction.create(
            {
                "name": "Override Rule - Max 50",
                "max_qty": 50.0,
                "is_max_mandatory": True,
            }
        )

        # 3. Mandatory Multiple Rule: Multiple 3 (Mandatory)
        cls.rule_multiple_mandatory = cls.Restriction.create(
            {
                "name": "Mandatory Multiple 3 Rule",
                "multiple_qty": 3.0,
                "is_multiple_mandatory": True,
            }
        )

        # 4. Warning Test Rule (Non-Mandatory): Min 5, Max 15, Multiple 2
        cls.rule_warning_only = cls.Restriction.create(
            {
                "name": "Warning Only Rule",
                "min_qty": 5.0,
                "is_min_mandatory": False,
                "max_qty": 15.0,
                "is_max_mandatory": False,
                "multiple_qty": 2.0,
                "is_multiple_mandatory": False,
            }
        )

        # 5. Rule with no constraints set
        cls.rule_no_restriction = cls.Restriction.create({})

        # --- Category and Products ---
        cls.category_a = cls.Category.create(
            {
                "name": "Category A",
                "manual_quantity_restriction_id": cls.rule_category_min.id,
            }
        )

        cls.product_a = cls.Product.create(
            {
                "name": "Product A (Min 10 Cat)",
                "type": "service",
                "categ_id": cls.category_a.id,
            }
        )

        cls.product_b = cls.Product.create(
            {
                "name": "Product B (No Category)",
                "type": "service",
            }
        )

        # --- Sale Order ---
        cls.sale_order = cls.env["sale.order"].create(
            {"partner_id": cls.env.ref("base.res_partner_1").id}
        )

    # -------------------------------------------------------------------
    # Tests on Inheritance and Override (product.template)
    # -------------------------------------------------------------------

    def test_01_template_inheritance(self):
        self.assertEqual(self.product_a.quantity_restriction_id, self.rule_category_min)

    def test_02_template_override_and_reset(self):
        """Tests if manual override works and if resetting restores inheritance."""

        # 1. Manual Override with Max 50 rule
        self.product_a.manual_quantity_restriction_id = self.rule_override_max
        self.assertEqual(self.product_a.quantity_restriction_id, self.rule_override_max)

        # 2. Test Reset: remove the override
        self.product_a.manual_quantity_restriction_id = False
        self.assertEqual(self.product_a.quantity_restriction_id, self.rule_category_min)

    # -------------------------------------------------------------------
    # Tests on Mandatory Validation (sale.order.line)
    # -------------------------------------------------------------------

    def test_03_mandatory_validation_min_on_create_and_write(self):
        """Tests the blocking validation (Mandatory Min) on creation and modification"""

        # Applied Rule: Mandatory Min 10 (Product A)

        # 1. Test on Create: Fail (qty < 10)
        with self.assertRaisesRegex(
            ValidationError, "lower than the MANDATORY minimum quantity of 10.0"
        ):
            self.SaleOrderLine.create(
                {
                    "order_id": self.sale_order.id,
                    "product_id": self.product_a.id,
                    "product_uom_qty": 5.0,
                }
            )

        # 2. Test on Create: Success
        line = self.SaleOrderLine.create(
            {
                "order_id": self.sale_order.id,
                "product_id": self.product_a.id,
                "product_uom_qty": 15.0,
            }
        )
        self.assertEqual(line.product_uom_qty, 15.0)

        # 3. Test on Write: Fail (new qty < 10)
        with self.assertRaisesRegex(
            ValidationError, "lower than the MANDATORY minimum quantity of 10.0"
        ):
            line.product_uom_qty = 8.0

    def test_04_mandatory_validation_max_on_create_and_write(self):
        """Tests the blocking validation (Mandatory Max)."""

        # Apply Mandatory Max 50 rule to Product B
        self.product_b.quantity_restriction_id = self.rule_override_max

        # 1. Test on Create: Fail (qty > 50)
        with self.assertRaisesRegex(
            ValidationError, "higher than the MANDATORY maximum quantity of 50.0"
        ):
            self.SaleOrderLine.create(
                {
                    "order_id": self.sale_order.id,
                    "product_id": self.product_b.id,
                    "product_uom_qty": 55.0,
                }
            )

        # 2. Test on Create: Success
        line = self.SaleOrderLine.create(
            {
                "order_id": self.sale_order.id,
                "product_id": self.product_b.id,
                "product_uom_qty": 45.0,
            }
        )
        self.assertEqual(line.product_uom_qty, 45.0)

        # 3. Test on Write: Fail (new qty > 50)
        with self.assertRaisesRegex(
            ValidationError, "higher than the MANDATORY maximum quantity of 50.0"
        ):
            line.product_uom_qty = 60.0

    def test_05_mandatory_validation_multiple(self):
        """Tests the blocking validation (Mandatory Multiple)."""

        # Apply Mandatory Multiple 3 rule to Product B
        self.product_b.quantity_restriction_id = self.rule_multiple_mandatory

        # 1. Test on Create: Fail (Quantity 4 is not a multiple of 3)
        with self.assertRaisesRegex(
            ValidationError, "must be a MANDATORY multiple of 3.0"
        ):
            self.SaleOrderLine.create(
                {
                    "order_id": self.sale_order.id,
                    "product_id": self.product_b.id,
                    "product_uom_qty": 4.0,
                }
            )

        # 2. Test on Create: Success
        line_ok = self.SaleOrderLine.create(
            {
                "order_id": self.sale_order.id,
                "product_id": self.product_b.id,
                "product_uom_qty": 6.0,
            }
        )
        self.assertEqual(line_ok.product_uom_qty, 6.0)

    # -------------------------------------------------------------------
    # Tests on Warnings (Yellow Line - Non-Mandatory)
    # -------------------------------------------------------------------

    def test_06_non_mandatory_warning(self):
        """Tests the warning_sale_qty field for all non-mandatory violations."""

        # Warning Test Rule (Min 5, Max 15, Multiple 2, all Non-Mandatory)
        self.product_b.quantity_restriction_id = self.rule_warning_only

        # 1. Compliant (Qty=10)
        line = self.SaleOrderLine.create(
            {
                "order_id": self.sale_order.id,
                "product_id": self.product_b.id,
                "product_uom_qty": 10.0,
            }
        )
        self.assertFalse(line.warning_sale_qty, "No warning expected (10 is OK).")

        # 2. Violation of Non-Mandatory Min (Qty=4)
        line.product_uom_qty = 4.0
        line._compute_warning_sale_qty()
        self.assertTrue(line.warning_sale_qty, "Warning expected (Qty < Min 5).")

        # 3. Violation of Non-Mandatory Max (Qty=20)
        line.product_uom_qty = 20.0
        line._compute_warning_sale_qty()
        self.assertTrue(line.warning_sale_qty, "Warning expected (Qty > Max 15).")

        # 4. Violation of Non-Mandatory Multiple (Qty=11)
        line.product_uom_qty = 11.0  # Min OK, Max OK, Multiple KO
        line._compute_warning_sale_qty()
        self.assertTrue(
            line.warning_sale_qty, "Warning expected (Qty not multiple of 2)."
        )

        # 5. Return to compliance (Qty=12)
        line.product_uom_qty = 12.0
        line._compute_warning_sale_qty()
        self.assertFalse(line.warning_sale_qty, "No warning expected (Qty 12 is OK).")

    # -------------------------------------------------------------------
    # Tests on Computed Name (sale.quantity.restriction)
    # -------------------------------------------------------------------

    def test_07_compute_rule_name(self):
        """Tests the _compute_name method with various scenarios."""

        # 1. Test Min/Max/Multiple (all Mandatory)
        combined_rule = self.Restriction.create(
            {
                "min_qty": 5.0,
                "is_min_mandatory": True,
                "max_qty": 100.0,
                "is_max_mandatory": True,
                "multiple_qty": 2.0,
                "is_multiple_mandatory": True,
            }
        )
        self.assertEqual(
            combined_rule.name, "Min: 5 (M), Max: 100 (M), Multiple: 2 (M)"
        )

        # 2. Test with decimal numbers
        decimal_rule = self.Restriction.create(
            {
                "min_qty": 1.5,
                "max_qty": 10.5,
                "multiple_qty": 0.5,  # Should be ignored because <= 1.0
            }
        )
        self.assertEqual(decimal_rule.name, "Min: 1.5, Max: 10.5")

        # 3. Test for rule with no restrictions set
        self.assertEqual(self.rule_no_restriction.name, "No Restriction")

        # 4.Test for float number that should display as an integer (using :g specifier)
        float_as_int_rule = self.Restriction.create({"min_qty": 10.0})
        self.assertEqual(float_as_int_rule.name, "Min: 10")
