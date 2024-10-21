# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestProductTemplate(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ProductCategory = cls.env["product.category"]
        cls.ProductTemplate = cls.env["product.template"]

    def test_inheritance(self):
        category = self.ProductCategory.create(
            {
                "name": "Category",
            }
        )
        self.assertEqual(category.is_sale_min_qty_set, False)
        self.assertEqual(category.sale_min_qty, 0.0)
        self.assertEqual(category.is_sale_restrict_min_qty_set, False)
        self.assertEqual(category.sale_restrict_min_qty, "0")
        self.assertEqual(category.is_sale_max_qty_set, False)
        self.assertEqual(category.sale_max_qty, 0.0)
        self.assertEqual(category.is_sale_restrict_max_qty_set, False)
        self.assertEqual(category.sale_restrict_max_qty, "0")
        self.assertEqual(category.is_sale_multiple_of_qty_set, False)
        self.assertEqual(category.sale_multiple_of_qty, 0.0)
        self.assertEqual(category.is_sale_restrict_multiple_of_qty_set, False)
        self.assertEqual(category.sale_restrict_multiple_of_qty, "0")

        template = self.ProductTemplate.create(
            {
                "name": "Child",
            }
        )
        self.assertEqual(template.is_sale_min_qty_set, False)
        self.assertEqual(template.sale_min_qty, 0.0)
        self.assertEqual(template.is_sale_restrict_min_qty_set, False)
        self.assertEqual(template.sale_restrict_min_qty, "0")
        self.assertEqual(template.is_sale_max_qty_set, False)
        self.assertEqual(template.sale_max_qty, 0.0)
        self.assertEqual(template.is_sale_restrict_max_qty_set, False)
        self.assertEqual(template.sale_restrict_max_qty, "0")
        self.assertEqual(template.is_sale_multiple_of_qty_set, False)
        self.assertEqual(template.sale_multiple_of_qty, 0.0)
        self.assertEqual(template.is_sale_restrict_multiple_of_qty_set, False)
        self.assertEqual(template.sale_restrict_multiple_of_qty, "0")

        template.update(
            {
                "categ_id": category.id,
            }
        )
        self.assertEqual(template.is_sale_min_qty_set, False)
        self.assertEqual(template.sale_min_qty, 0.0)
        self.assertEqual(template.is_sale_restrict_min_qty_set, False)
        self.assertEqual(template.sale_restrict_min_qty, "0")
        self.assertEqual(template.is_sale_max_qty_set, False)
        self.assertEqual(template.sale_max_qty, 0.0)
        self.assertEqual(template.is_sale_restrict_max_qty_set, False)
        self.assertEqual(template.sale_restrict_max_qty, "0")
        self.assertEqual(template.is_sale_multiple_of_qty_set, False)
        self.assertEqual(template.sale_multiple_of_qty, 0.0)
        self.assertEqual(template.is_sale_restrict_multiple_of_qty_set, False)
        self.assertEqual(template.sale_restrict_multiple_of_qty, "0")

        category.update(
            {
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": "1",
                "sale_max_qty": 100.0,
                "sale_restrict_max_qty": "1",
                "sale_multiple_of_qty": 5.0,
                "sale_restrict_multiple_of_qty": "1",
            }
        )
        self.assertTrue(template.is_sale_min_qty_set)
        self.assertTrue(template.is_sale_restrict_min_qty_set)
        self.assertTrue(template.is_sale_max_qty_set)
        self.assertTrue(template.is_sale_restrict_max_qty_set)
        self.assertTrue(template.is_sale_multiple_of_qty_set)
        self.assertTrue(template.is_sale_restrict_multiple_of_qty_set)
        self.assertFalse(template.is_sale_own_min_qty_set)
        self.assertFalse(template.is_sale_own_restrict_min_qty_set)
        self.assertFalse(template.is_sale_own_max_qty_set)
        self.assertFalse(template.is_sale_own_restrict_max_qty_set)
        self.assertFalse(template.is_sale_own_multiple_of_qty_set)
        self.assertFalse(template.is_sale_own_restrict_multiple_of_qty_set)
        self.assertEqual(template.sale_min_qty, 10.0)
        self.assertEqual(template.sale_restrict_min_qty, "1")
        self.assertEqual(template.sale_max_qty, 100.0)
        self.assertEqual(template.sale_restrict_max_qty, "1")
        self.assertEqual(template.sale_multiple_of_qty, 5.0)
        self.assertEqual(template.sale_restrict_multiple_of_qty, "1")

        template.sale_min_qty = 20.0
        self.assertTrue(template.is_sale_own_min_qty_set)
        self.assertEqual(template.sale_own_min_qty, 20.0)

        template.sale_restrict_min_qty = "0"
        self.assertTrue(template.is_sale_own_restrict_min_qty_set)
        self.assertEqual(template.sale_own_restrict_min_qty, "0")

        template.sale_max_qty = 200.0
        self.assertTrue(template.is_sale_own_max_qty_set)
        self.assertEqual(template.sale_own_max_qty, 200.0)

        template.sale_restrict_max_qty = "0"
        self.assertTrue(template.is_sale_own_restrict_max_qty_set)
        self.assertEqual(template.sale_own_restrict_max_qty, "0")

        template.sale_multiple_of_qty = 10.0
        self.assertTrue(template.is_sale_own_multiple_of_qty_set)
        self.assertEqual(template.sale_own_multiple_of_qty, 10.0)

        template.sale_restrict_multiple_of_qty = "0"
        self.assertTrue(template.is_sale_own_restrict_multiple_of_qty_set)
        self.assertEqual(template.sale_own_restrict_multiple_of_qty, "0")

        template.is_sale_own_min_qty_set = False
        template._onchange_is_sale_min_qty_set()
        self.assertEqual(template.sale_min_qty, 10.0)
        self.assertEqual(template.sale_own_min_qty, 0.0)

        template.is_sale_own_restrict_min_qty_set = False
        self.assertEqual(template.sale_restrict_min_qty, "1")
        self.assertFalse(template.sale_own_restrict_min_qty)

        template.is_sale_own_max_qty_set = False
        template._onchange_is_sale_max_qty_set()
        self.assertEqual(template.sale_max_qty, 100.0)
        self.assertEqual(template.sale_own_max_qty, 0.0)

        template.is_sale_own_restrict_max_qty_set = False
        self.assertEqual(template.sale_restrict_max_qty, "1")
        self.assertFalse(template.sale_own_restrict_max_qty)

        template.is_sale_own_multiple_of_qty_set = False
        template._onchange_is_sale_multiple_of_qty_set()
        self.assertEqual(template.sale_multiple_of_qty, 5.0)
        self.assertEqual(template.sale_own_multiple_of_qty, 0.0)

        template.is_sale_own_restrict_multiple_of_qty_set = False
        self.assertEqual(template.sale_restrict_multiple_of_qty, "1")
        self.assertFalse(template.sale_own_restrict_multiple_of_qty)
