# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestProductAssortment(TransactionCase):
    def setUp(self):
        super().setUp()
        self.filter_obj = self.env["ir.filters"]
        self.product_obj = self.env["product.product"]
        self.sale_order_obj = self.env["sale.order"]
        self.partner_1 = self.env["res.partner"].create({"name": "Test partner 1"})
        self.partner_2 = self.env["res.partner"].create({"name": "Test partner 2"})

    def test_sale_order_product_assortment(self):
        product_1 = self.product_obj.create({"name": "Test product 1"})
        product_2 = self.product_obj.create({"name": "Test product 2"})
        assortment_with_whitelist = self.filter_obj.create(
            {
                "name": "Test Assortment 1",
                "model_id": "product.product",
                "domain": [],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id)],
                "whitelist_product_ids": [(4, product_1.id)],
            }
        )
        sale_order_1 = self.sale_order_obj.create(
            {
                "partner_id": self.partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_1.id,
                        },
                    )
                ],
            }
        )
        self.assertEqual(
            sale_order_1.allowed_product_ids,
            assortment_with_whitelist.whitelist_product_ids,
        )
        self.assertTrue(sale_order_1.has_allowed_products)
        self.filter_obj.create(
            {
                "name": "Test Assortment 2",
                "model_id": "product.product",
                "domain": [],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id)],
                "blacklist_product_ids": [(4, product_2.id)],
                "partner_domain": "[('id', '=', %s)]" % self.partner_2.id,
            }
        )
        sale_order_2 = self.sale_order_obj.create(
            {
                "partner_id": self.partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_1.id,
                        },
                    )
                ],
            }
        )
        self.assertNotIn(product_2, sale_order_2.allowed_product_ids)
        self.assertTrue(sale_order_2.has_allowed_products)
        sale_order_3 = self.sale_order_obj.create({"partner_id": self.partner_2.id})
        self.assertFalse(sale_order_3.has_allowed_products)
        self.assertNotIn(product_2, sale_order_3.allowed_product_ids)

        so = Form(self.env["sale.order"])
        with so.order_line.new() as line:
            line.product_id = product_2

        # Changing the partner while having an order line
        # with a product that doesn't belong to the partner
        # should raise an error
        with self.assertRaises(UserError):
            so.partner_id = self.partner_1

    def test_sale_order_multiple_assortment(self):
        product_1 = self.product_obj.create({"name": "Test product 1"})
        product_2 = self.product_obj.create({"name": "Test product 2"})
        product_3 = self.product_obj.create({"name": "Test product 3"})
        product_4 = self.product_obj.create({"name": "Test product 4"})

        self.filter_obj.create(
            {
                "name": "Test Assortment 1",
                "model_id": "product.product",
                "domain": [("id", "in", [product_1.id, product_2.id])],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id)],
                "blacklist_product_ids": [(4, product_4.id)],
            }
        )

        self.filter_obj.create(
            {
                "name": "Test Assortment 2",
                "model_id": "product.product",
                "domain": [("id", "in", [product_3.id, product_4.id])],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id)],
                "blacklist_product_ids": [(4, product_2.id)],
            }
        )

        sale_order_1 = self.sale_order_obj.create(
            {
                "partner_id": self.partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_1.id,
                        },
                    )
                ],
            }
        )
        self.assertListEqual(
            sale_order_1.allowed_product_ids.ids,
            [product_1.id, product_3.id],
        )
