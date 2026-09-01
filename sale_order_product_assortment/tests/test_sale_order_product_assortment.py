# Copyright 2020 Tecnativa - Carlos Roca
# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Domain
from odoo.tests.common import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestProductAssortment(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.filter_obj = cls.env["ir.filters"]
        cls.product_obj = cls.env["product.product"]
        cls.sale_order_obj = cls.env["sale.order"]
        cls.partner_1 = cls.env["res.partner"].create({"name": "Test partner 1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Test partner 2"})

    def test_sale_order_product_assortment(self):
        product_1 = self.product_obj.create({"name": "Test product 1"})
        product_2 = self.product_obj.create({"name": "Test product 2"})
        product_3 = self.product_obj.create({"name": "Test product 3"})
        assortment_with_whitelist = self.filter_obj.create(
            {
                "name": "Test Assortment 1",
                "model_id": "product.product",
                "domain": [("id", "=", 0)],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id)],
                "whitelist_product_ids": [(4, product_1.id)],
            }
        )
        self.partner_1._update_partner_assortments()
        sale_order_1 = self.sale_order_obj.create({"partner_id": self.partner_1.id})
        self.assertEqual(
            sale_order_1.allowed_product_ids,
            assortment_with_whitelist.whitelist_product_ids,
        )
        self.assertTrue(sale_order_1.has_allowed_products)
        self.filter_obj.create(
            {
                "name": "Test Assortment 2",
                "model_id": "product.product",
                "domain": [("id", "=", 0)],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id)],
                "blacklist_product_ids": [(4, product_2.id)],
                "partner_domain": f"[('id', '=', {self.partner_2.id})]",
                "apply_black_list_product_domain": True,
                "black_list_product_domain": [("id", "=", product_3.id)],
            }
        )
        self.partner_1._update_partner_assortments()
        self.partner_2._update_partner_assortments()
        sale_order_2 = self.sale_order_obj.create({"partner_id": self.partner_1.id})
        self.assertNotIn(product_2, sale_order_2.allowed_product_ids)
        self.assertTrue(sale_order_2.has_allowed_products)
        sale_order_3 = self.sale_order_obj.create({"partner_id": self.partner_2.id})
        self.assertTrue(sale_order_3.has_allowed_products)
        self.assertNotIn(product_2, sale_order_3.allowed_product_ids)
        self.assertNotIn(product_3, sale_order_3.allowed_product_ids)

    def test_get_product_catalog_domain(self):
        product_allowed = self.product_obj.create(
            {"name": "Catalog allowed product", "sale_ok": True}
        )
        product_other = self.product_obj.create(
            {"name": "Catalog other product", "sale_ok": True}
        )
        sale_order_no_assortment = self.sale_order_obj.create(
            {"partner_id": self.partner_2.id}
        )
        self.assertFalse(sale_order_no_assortment.has_allowed_products)
        self.assertEqual(
            sale_order_no_assortment._get_product_catalog_domain(),
            super(
                type(sale_order_no_assortment), sale_order_no_assortment
            )._get_product_catalog_domain(),
        )
        catalog_products = self.product_obj.search(
            sale_order_no_assortment._get_product_catalog_domain()
        )
        self.assertIn(product_allowed, catalog_products)
        self.assertIn(product_other, catalog_products)

        self.filter_obj.create(
            {
                "name": "Catalog Assortment",
                "model_id": "product.product",
                "domain": [("id", "=", 0)],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id)],
                "whitelist_product_ids": [(4, product_allowed.id)],
            }
        )
        self.partner_1._update_partner_assortments()
        sale_order_assortment = self.sale_order_obj.create(
            {"partner_id": self.partner_1.id}
        )
        self.assertTrue(sale_order_assortment.has_allowed_products)
        super_domain = sale_order_no_assortment._get_product_catalog_domain()
        expected_domain = Domain.AND(
            [
                super_domain,
                [("id", "in", sale_order_assortment.allowed_product_ids.ids)],
            ]
        )
        self.assertEqual(
            sale_order_assortment._get_product_catalog_domain(), expected_domain
        )
        catalog_products = self.product_obj.search(
            sale_order_assortment._get_product_catalog_domain()
        )
        self.assertIn(product_allowed, catalog_products)
        self.assertNotIn(product_other, catalog_products)
        return True
