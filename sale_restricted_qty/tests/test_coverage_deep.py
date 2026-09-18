# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestCoverageDeep(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductCategory = cls.env["product.category"]
        cls.ProductTemplate = cls.env["product.template"]
        cls.Product = cls.env["product.product"]

    def test_exhaustive_mixin_paths(self):
        """Hit all branches in the mixin using a template."""
        template = self.ProductTemplate.create({"name": "Test Template"})

        for field_prefix in ["min_qty", "max_qty", "multiple_of_qty"]:
            # 1. Test Value logic
            val_field = f"sale_{field_prefix}"
            own_val_field = f"sale_own_{field_prefix}"
            own_set_field = f"is_sale_own_{field_prefix}_set"
            onchange_val = f"_onchange_is_sale_{field_prefix}_set"

            # Inverse: Set value
            setattr(template, val_field, 10.0)
            self.assertTrue(getattr(template, own_set_field))
            self.assertEqual(getattr(template, own_val_field), 10.0)

            # Inverse: Reset to 0 (or inherited) -> unsets
            setattr(template, val_field, 0.0)
            self.assertFalse(getattr(template, own_set_field))
            self.assertEqual(getattr(template, own_val_field), 0.0)

            # Onchange: Set
            setattr(template, own_set_field, True)
            getattr(template, onchange_val)()
            # Onchange: Unset
            setattr(template, own_set_field, False)
            getattr(template, onchange_val)()

            # 2. Test Restrict logic
            restrict_field = f"sale_restrict_{field_prefix}"
            own_restrict_field = f"sale_own_restrict_{field_prefix}"
            own_restrict_set_field = f"is_sale_own_restrict_{field_prefix}_set"
            onchange_restrict = f"_onchange_is_sale_restrict_{field_prefix}_set"
            inverse_restrict_set = f"_inverse_is_sale_own_restrict_{field_prefix}_set"

            # Inverse: Set restriction
            setattr(template, restrict_field, "1")
            self.assertTrue(getattr(template, own_restrict_set_field))
            self.assertEqual(getattr(template, own_restrict_field), "1")

            # Test the boolean flag inverse explicitly
            setattr(template, own_restrict_set_field, True)
            getattr(template, inverse_restrict_set)()

            setattr(template, own_restrict_set_field, False)
            getattr(template, inverse_restrict_set)()

            # Onchange: Set
            setattr(template, own_restrict_set_field, True)
            getattr(template, onchange_restrict)()
            # Onchange: Unset
            setattr(template, own_restrict_set_field, False)
            getattr(template, onchange_restrict)()

    def test_model_overrides_coverage(self):
        """Hit the 12 compute methods in each model by changing hierarchy."""
        # 1. Category hierarchy
        parent = self.ProductCategory.create({"name": "Parent"})
        child = self.ProductCategory.create({"name": "Child", "parent_id": parent.id})

        # Trigger all 12 computes on child by modifying parent
        parent.write(
            {
                "sale_min_qty": 1.0,
                "sale_restrict_min_qty": "1",
                "sale_max_qty": 2.0,
                "sale_restrict_max_qty": "1",
                "sale_multiple_of_qty": 3.0,
                "sale_restrict_multiple_of_qty": "1",
            }
        )
        self.assertEqual(child.sale_min_qty, 1.0)
        self.assertEqual(child.sale_max_qty, 2.0)
        self.assertEqual(child.sale_multiple_of_qty, 3.0)

        # Test the "not parent_id" branch for all types (hits super())
        for pf in ["min", "max", "multiple_of"]:
            self.assertFalse(getattr(parent, f"is_sale_inherited_{pf}_qty_set"))
            self.assertEqual(getattr(parent, f"sale_inherited_{pf}_qty"), 0.0)

        # 2. Template / Product variants
        template = self.ProductTemplate.create(
            {
                "name": "Template",
                "categ_id": child.id,
            }
        )
        product = template.product_variant_id

        # Trigger computes by changing template
        template.write({"sale_min_qty": 5.0})
        self.assertEqual(product.sale_min_qty, 5.0)

        # Clear parent values to stop inheritance (all fields)
        parent.write(
            {
                "sale_min_qty": 0.0,
                "sale_restrict_min_qty": "0",
                "sale_max_qty": 0.0,
                "sale_restrict_max_qty": "0",
                "sale_multiple_of_qty": 0.0,
                "sale_restrict_multiple_of_qty": "0",
            }
        )
        # Also clear the template's own value, otherwise product
        # still inherits from template
        template.write({"sale_min_qty": 0.0})
        template.invalidate_recordset()

        # Test "no parent" cases for Template and Product for all types
        for pf in ["min", "max", "multiple_of"]:
            self.assertFalse(getattr(template, f"is_sale_inherited_{pf}_qty_set"))
            self.assertFalse(getattr(product, f"is_sale_inherited_{pf}_qty_set"))

        # 3. Test edge case: no product_tmpl_id
        # (should not normally happen, but for coverage)
        product.product_tmpl_id = False
        for pf in ["min", "max", "multiple_of"]:
            self.assertFalse(getattr(product, f"is_sale_inherited_{pf}_qty_set"))
            self.assertEqual(getattr(product, f"sale_inherited_{pf}_qty"), 0.0)

    def test_sale_order_line_onchanges_deep(self):
        """Cover all branches of SO line onchanges."""
        product = self.Product.create(
            {
                "name": "Product",
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": "1",
            }
        )
        line = self.env["sale.order.line"].new({"product_id": product.id})

        # Hits the "1.0" branch
        line.product_uom_qty = 1.0
        line._onchange_product_id_set_min_qty()
        self.assertEqual(line.product_uom_qty, 10.0)

        # Hits the "0.0" branch
        line.product_uom_qty = 0.0
        line._onchange_product_id_set_min_qty()
        self.assertEqual(line.product_uom_qty, 10.0)

        # Hits the "already set" branch (no overwrite)
        line.product_uom_qty = 5.0
        line._onchange_product_id_set_min_qty()
        self.assertEqual(line.product_uom_qty, 5.0)

        # Hits the "not enforced" branch
        product.sale_restrict_min_qty = "0"

        # New line to pick up the change
        line2 = self.env["sale.order.line"].new({"product_id": product.id})
        # Force recompute of line fields from product
        line2._compute_restricted_qty_from_product()

        line2.product_uom_qty = 1.0
        line2._onchange_product_id_set_min_qty()
        self.assertEqual(line2.product_uom_qty, 1.0)

    def test_onchange_no_product(self):
        """Test onchange with no product set (coverage edge case)."""
        # Initialize with 0.0 to ensure it doesn't default to 1.0 (Odoo default)
        line = self.env["sale.order.line"].new({"product_uom_qty": 0.0})
        line._onchange_product_id_set_min_qty()
        # Should not crash and do nothing
        self.assertFalse(line.product_uom_qty)
