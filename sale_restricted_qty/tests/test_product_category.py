# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestProductCategory(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ProductCategory = cls.env["product.category"]

    def test_inheritance(self):
        parent = self.ProductCategory.create(
            {
                "name": "Parent",
            }
        )
        self.assertEqual(parent.is_sale_min_qty_set, False)
        self.assertEqual(parent.sale_min_qty, 0.0)
        self.assertEqual(parent.is_sale_restrict_min_qty_set, False)
        self.assertEqual(parent.sale_restrict_min_qty, "0")
        self.assertEqual(parent.is_sale_max_qty_set, False)
        self.assertEqual(parent.sale_max_qty, 0.0)
        self.assertEqual(parent.is_sale_restrict_max_qty_set, False)
        self.assertEqual(parent.sale_restrict_max_qty, "0")
        self.assertEqual(parent.is_sale_multiple_of_qty_set, False)
        self.assertEqual(parent.sale_multiple_of_qty, 0.0)
        self.assertEqual(parent.is_sale_restrict_multiple_of_qty_set, False)
        self.assertEqual(parent.sale_restrict_multiple_of_qty, "0")

        child = self.ProductCategory.create(
            {
                "name": "Child",
                "parent_id": parent.id,
            }
        )
        self.assertEqual(child.sale_min_qty, 0.0)
        self.assertEqual(child.sale_restrict_min_qty, "0")
        self.assertEqual(child.sale_max_qty, 0.0)
        self.assertEqual(child.sale_restrict_max_qty, "0")
        self.assertEqual(child.sale_multiple_of_qty, 0.0)
        self.assertEqual(child.sale_restrict_multiple_of_qty, "0")

        parent.update(
            {
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": "1",
                "sale_max_qty": 100.0,
                "sale_restrict_max_qty": "1",
                "sale_multiple_of_qty": 5.0,
                "sale_restrict_multiple_of_qty": "1",
            }
        )
        self.assertTrue(child.is_sale_min_qty_set)
        self.assertTrue(child.is_sale_restrict_min_qty_set)
        self.assertTrue(child.is_sale_max_qty_set)
        self.assertTrue(child.is_sale_restrict_max_qty_set)
        self.assertTrue(child.is_sale_multiple_of_qty_set)
        self.assertTrue(child.is_sale_restrict_multiple_of_qty_set)
        self.assertFalse(child.is_sale_own_min_qty_set)
        self.assertFalse(child.is_sale_own_restrict_min_qty_set)
        self.assertFalse(child.is_sale_own_max_qty_set)
        self.assertFalse(child.is_sale_own_restrict_max_qty_set)
        self.assertFalse(child.is_sale_own_multiple_of_qty_set)
        self.assertFalse(child.is_sale_own_restrict_multiple_of_qty_set)
        self.assertEqual(child.sale_min_qty, 10.0)
        self.assertEqual(child.sale_restrict_min_qty, "1")
        self.assertEqual(child.sale_max_qty, 100.0)
        self.assertEqual(child.sale_restrict_max_qty, "1")
        self.assertEqual(child.sale_multiple_of_qty, 5.0)
        self.assertEqual(child.sale_restrict_multiple_of_qty, "1")

        child.sale_min_qty = 20.0
        self.assertTrue(child.is_sale_own_min_qty_set)
        self.assertEqual(child.sale_own_min_qty, 20.0)

        child.sale_restrict_min_qty = "0"
        self.assertTrue(child.is_sale_own_restrict_min_qty_set)
        self.assertEqual(child.sale_own_restrict_min_qty, "0")

        child.sale_max_qty = 200.0
        self.assertTrue(child.is_sale_own_max_qty_set)
        self.assertEqual(child.sale_own_max_qty, 200.0)

        child.sale_restrict_max_qty = "0"
        self.assertTrue(child.is_sale_own_restrict_max_qty_set)
        self.assertEqual(child.sale_own_restrict_max_qty, "0")

        child.sale_multiple_of_qty = 10.0
        self.assertTrue(child.is_sale_own_multiple_of_qty_set)
        self.assertEqual(child.sale_own_multiple_of_qty, 10.0)

        child.sale_restrict_multiple_of_qty = "0"
        self.assertTrue(child.is_sale_own_restrict_multiple_of_qty_set)
        self.assertEqual(child.sale_own_restrict_multiple_of_qty, "0")

        child.is_sale_own_min_qty_set = False
        child._onchange_is_sale_min_qty_set()
        self.assertEqual(child.sale_min_qty, 10.0)
        self.assertEqual(child.sale_own_min_qty, 0.0)

        child.is_sale_own_restrict_min_qty_set = False
        self.assertEqual(child.sale_restrict_min_qty, "1")
        self.assertFalse(child.sale_own_restrict_min_qty)

        child.is_sale_own_max_qty_set = False
        child._onchange_is_sale_max_qty_set()
        self.assertEqual(child.sale_max_qty, 100.0)
        self.assertEqual(child.sale_own_max_qty, 0.0)

        child.is_sale_own_restrict_max_qty_set = False
        self.assertEqual(child.sale_restrict_max_qty, "1")
        self.assertFalse(child.sale_own_restrict_max_qty)

        child.is_sale_own_multiple_of_qty_set = False
        child._onchange_is_sale_multiple_of_qty_set()
        self.assertEqual(child.sale_multiple_of_qty, 5.0)
        self.assertEqual(child.sale_own_multiple_of_qty, 0.0)

        child.is_sale_own_restrict_multiple_of_qty_set = False
        self.assertEqual(child.sale_restrict_multiple_of_qty, "1")
        self.assertFalse(child.sale_own_restrict_multiple_of_qty)
