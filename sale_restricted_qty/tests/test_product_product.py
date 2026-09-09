# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.tests import tagged

from odoo.addons.sale_restricted_qty.models.product_restricted_qty_mixin import (
    RESTRICTION_DISABLED,
    RESTRICTION_ENABLED,
)


@tagged("post_install", "-at_install")
class TestProductTemplate(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ProductTemplate = cls.env["product.template"]
        cls.Product = cls.env["product.product"]

    def test_inheritance(self):
        template = self.ProductTemplate.create(
            {
                "name": "Template",
            }
        )
        self.assertEqual(template.is_sale_min_qty_set, False)
        self.assertEqual(template.sale_min_qty, 0.0)
        self.assertEqual(template.is_sale_restrict_min_qty_set, False)
        self.assertEqual(template.sale_restrict_min_qty, RESTRICTION_DISABLED)
        self.assertEqual(template.is_sale_max_qty_set, False)
        self.assertEqual(template.sale_max_qty, 0.0)
        self.assertEqual(template.is_sale_restrict_max_qty_set, False)
        self.assertEqual(template.sale_restrict_max_qty, RESTRICTION_DISABLED)
        self.assertEqual(template.is_sale_multiple_of_qty_set, False)
        self.assertEqual(template.sale_multiple_of_qty, 0.0)
        self.assertEqual(template.is_sale_restrict_multiple_of_qty_set, False)
        self.assertEqual(template.sale_restrict_multiple_of_qty, RESTRICTION_DISABLED)

        product = template.product_variant_id
        product.write(
            {
                "name": "Product",
            }
        )
        self.assertEqual(product.sale_min_qty, 0.0)
        self.assertEqual(product.sale_restrict_min_qty, RESTRICTION_DISABLED)
        self.assertEqual(product.sale_max_qty, 0.0)
        self.assertEqual(product.sale_restrict_max_qty, RESTRICTION_DISABLED)
        self.assertEqual(product.sale_multiple_of_qty, 0.0)
        self.assertEqual(product.sale_restrict_multiple_of_qty, RESTRICTION_DISABLED)

        template.update(
            {
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": RESTRICTION_ENABLED,
                "sale_max_qty": 100.0,
                "sale_restrict_max_qty": RESTRICTION_ENABLED,
                "sale_multiple_of_qty": 5.0,
                "sale_restrict_multiple_of_qty": RESTRICTION_ENABLED,
            }
        )
        self.assertTrue(product.is_sale_min_qty_set)
        self.assertTrue(product.is_sale_restrict_min_qty_set)
        self.assertTrue(product.is_sale_max_qty_set)
        self.assertTrue(product.is_sale_restrict_max_qty_set)
        self.assertTrue(product.is_sale_multiple_of_qty_set)
        self.assertTrue(product.is_sale_restrict_multiple_of_qty_set)
        self.assertFalse(product.is_sale_own_min_qty_set)
        self.assertFalse(product.is_sale_own_restrict_min_qty_set)
        self.assertFalse(product.is_sale_own_max_qty_set)
        self.assertFalse(product.is_sale_own_restrict_max_qty_set)
        self.assertFalse(product.is_sale_own_multiple_of_qty_set)
        self.assertFalse(product.is_sale_own_restrict_multiple_of_qty_set)
        self.assertEqual(product.sale_min_qty, 10.0)
        self.assertEqual(product.sale_restrict_min_qty, RESTRICTION_ENABLED)
        self.assertEqual(product.sale_max_qty, 100.0)
        self.assertEqual(product.sale_restrict_max_qty, RESTRICTION_ENABLED)
        self.assertEqual(product.sale_multiple_of_qty, 5.0)
        self.assertEqual(product.sale_restrict_multiple_of_qty, RESTRICTION_ENABLED)

        product.sale_min_qty = 20.0
        self.assertTrue(product.is_sale_own_min_qty_set)
        self.assertEqual(product.sale_own_min_qty, 20.0)

        product.sale_restrict_min_qty = RESTRICTION_DISABLED
        self.assertTrue(product.is_sale_own_restrict_min_qty_set)
        self.assertEqual(product.sale_own_restrict_min_qty, RESTRICTION_DISABLED)

        product.sale_max_qty = 200.0
        self.assertTrue(product.is_sale_own_max_qty_set)
        self.assertEqual(product.sale_own_max_qty, 200.0)

        product.sale_restrict_max_qty = RESTRICTION_DISABLED
        self.assertTrue(product.is_sale_own_restrict_max_qty_set)
        self.assertEqual(product.sale_own_restrict_max_qty, RESTRICTION_DISABLED)

        product.sale_multiple_of_qty = 10.0
        self.assertTrue(product.is_sale_own_multiple_of_qty_set)
        self.assertEqual(product.sale_own_multiple_of_qty, 10.0)

        product.sale_restrict_multiple_of_qty = RESTRICTION_DISABLED
        self.assertTrue(product.is_sale_own_restrict_multiple_of_qty_set)
        self.assertEqual(
            product.sale_own_restrict_multiple_of_qty, RESTRICTION_DISABLED
        )

        product.is_sale_own_min_qty_set = False
        product._onchange_is_sale_min_qty_set()
        self.assertEqual(product.sale_min_qty, 10.0)
        self.assertEqual(product.sale_own_min_qty, 0.0)

        product.is_sale_own_restrict_min_qty_set = False
        product._onchange_is_sale_restrict_min_qty_set()
        self.assertEqual(product.sale_restrict_min_qty, RESTRICTION_ENABLED)
        self.assertFalse(product.sale_own_restrict_min_qty)

        product.is_sale_own_max_qty_set = False
        product._onchange_is_sale_max_qty_set()
        self.assertEqual(product.sale_max_qty, 100.0)
        self.assertEqual(product.sale_own_max_qty, 0.0)

        product.is_sale_own_restrict_max_qty_set = False
        product._onchange_is_sale_restrict_max_qty_set()
        self.assertEqual(product.sale_restrict_max_qty, RESTRICTION_ENABLED)
        self.assertFalse(product.sale_own_restrict_max_qty)

        product.is_sale_own_multiple_of_qty_set = False
        product._onchange_is_sale_multiple_of_qty_set()
        self.assertEqual(product.sale_multiple_of_qty, 5.0)
        self.assertEqual(product.sale_own_multiple_of_qty, 0.0)

        product.is_sale_own_restrict_multiple_of_qty_set = False
        product._onchange_is_sale_restrict_multiple_of_qty_set()
        self.assertEqual(product.sale_restrict_multiple_of_qty, RESTRICTION_ENABLED)
        self.assertFalse(product.sale_own_restrict_multiple_of_qty)

    def test_variant_restrict_inheritance_and_override(self):
        """A variant inherits the template restrict, can override it, and
        follows the template again once the override is removed."""
        template = self.ProductTemplate.create(
            {
                "name": "Template",
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": RESTRICTION_DISABLED,  # Warning
            }
        )
        product = template.product_variant_id

        # Inherits, without an own override.
        self.assertFalse(product.is_sale_own_restrict_min_qty_set)
        self.assertEqual(product.sale_restrict_min_qty, RESTRICTION_DISABLED)

        # Explicit variant override is honoured...
        product.sale_restrict_min_qty = RESTRICTION_ENABLED
        self.assertTrue(product.is_sale_own_restrict_min_qty_set)
        self.assertEqual(product.sale_restrict_min_qty, RESTRICTION_ENABLED)

        # ...and removing it re-inherits the template value.
        product.is_sale_own_restrict_min_qty_set = False
        product._onchange_is_sale_restrict_min_qty_set()
        self.assertEqual(product.sale_restrict_min_qty, RESTRICTION_DISABLED)

        # Changing the template now propagates to the variant.
        template.sale_restrict_min_qty = RESTRICTION_ENABLED
        self.assertEqual(product.sale_restrict_min_qty, RESTRICTION_ENABLED)
