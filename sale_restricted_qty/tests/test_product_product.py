# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


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
        self.assertEqual(template.sale_restrict_min_qty, "0")
        self.assertEqual(template.is_sale_max_qty_set, False)
        self.assertEqual(template.sale_max_qty, 0.0)
        self.assertEqual(template.is_sale_restrict_max_qty_set, False)
        self.assertEqual(template.sale_restrict_max_qty, "0")
        self.assertEqual(template.is_sale_multiple_of_qty_set, False)
        self.assertEqual(template.sale_multiple_of_qty, 0.0)
        self.assertEqual(template.is_sale_restrict_multiple_of_qty_set, False)
        self.assertEqual(template.sale_restrict_multiple_of_qty, "0")

        product = self.Product.create(
            {
                "name": "Product",
                "product_tmpl_id": template.id,
            }
        )
        self.assertEqual(product.sale_min_qty, 0.0)
        self.assertEqual(product.sale_restrict_min_qty, "0")
        self.assertEqual(product.sale_max_qty, 0.0)
        self.assertEqual(product.sale_restrict_max_qty, "0")
        self.assertEqual(product.sale_multiple_of_qty, 0.0)
        self.assertEqual(product.sale_restrict_multiple_of_qty, "0")

        template.update(
            {
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": "1",
                "sale_max_qty": 100.0,
                "sale_restrict_max_qty": "1",
                "sale_multiple_of_qty": 5.0,
                "sale_restrict_multiple_of_qty": "1",
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
        self.assertEqual(product.sale_restrict_min_qty, "1")
        self.assertEqual(product.sale_max_qty, 100.0)
        self.assertEqual(product.sale_restrict_max_qty, "1")
        self.assertEqual(product.sale_multiple_of_qty, 5.0)
        self.assertEqual(product.sale_restrict_multiple_of_qty, "1")

        product.sale_min_qty = 20.0
        self.assertTrue(product.is_sale_own_min_qty_set)
        self.assertEqual(product.sale_own_min_qty, 20.0)

        product.sale_restrict_min_qty = "0"
        self.assertTrue(product.is_sale_own_restrict_min_qty_set)
        self.assertEqual(product.sale_own_restrict_min_qty, "0")

        product.sale_max_qty = 200.0
        self.assertTrue(product.is_sale_own_max_qty_set)
        self.assertEqual(product.sale_own_max_qty, 200.0)

        product.sale_restrict_max_qty = "0"
        self.assertTrue(product.is_sale_own_restrict_max_qty_set)
        self.assertEqual(product.sale_own_restrict_max_qty, "0")

        product.sale_multiple_of_qty = 10.0
        self.assertTrue(product.is_sale_own_multiple_of_qty_set)
        self.assertEqual(product.sale_own_multiple_of_qty, 10.0)

        product.sale_restrict_multiple_of_qty = "0"
        self.assertTrue(product.is_sale_own_restrict_multiple_of_qty_set)
        self.assertEqual(product.sale_own_restrict_multiple_of_qty, "0")

        product.is_sale_own_min_qty_set = False
        product._onchange_is_sale_min_qty_set()
        self.assertEqual(product.sale_min_qty, 10.0)
        self.assertEqual(product.sale_own_min_qty, 0.0)

        product.is_sale_own_restrict_min_qty_set = False
        self.assertEqual(product.sale_restrict_min_qty, "1")
        self.assertFalse(product.sale_own_restrict_min_qty)

        product.is_sale_own_max_qty_set = False
        product._onchange_is_sale_max_qty_set()
        self.assertEqual(product.sale_max_qty, 100.0)
        self.assertEqual(product.sale_own_max_qty, 0.0)

        product.is_sale_own_restrict_max_qty_set = False
        self.assertEqual(product.sale_restrict_max_qty, "1")
        self.assertFalse(product.sale_own_restrict_max_qty)

        product.is_sale_own_multiple_of_qty_set = False
        product._onchange_is_sale_multiple_of_qty_set()
        self.assertEqual(product.sale_multiple_of_qty, 5.0)
        self.assertEqual(product.sale_own_multiple_of_qty, 0.0)

        product.is_sale_own_restrict_multiple_of_qty_set = False
        self.assertEqual(product.sale_restrict_multiple_of_qty, "1")
        self.assertFalse(product.sale_own_restrict_multiple_of_qty)
