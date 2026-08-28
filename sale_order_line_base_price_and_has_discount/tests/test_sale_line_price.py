# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": "10.0",
            }
        )

        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "0_product_variant",
                            "product_id": cls.product.id,
                            "compute_price": "formula",
                            "base": "list_price",
                            "price_discount": 10,
                        }
                    )
                ],
            }
        )

        cls.pricelist_pro = cls.env["product.pricelist"].create(
            {
                "name": "Pro",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "3_global",
                            # "product_id": cls.product.id,
                            "compute_price": "formula",
                            "base": "pricelist",
                            "price_discount": 10,
                            "base_pricelist_id": cls.pricelist.id,
                        }
                    )
                ],
            }
        )

    def test_sale_price(self):
        order = self.env["sale.order"].create(
            {
                "pricelist_id": self.pricelist.id,
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                        }
                    )
                ],
            }
        )
        self.assertEqual(10.0, order.order_line.base_price)
        self.assertEqual(
            9.0,
            order.order_line.price_unit,
        )
        self.assertTrue(order.order_line.has_discount_price)
        self.assertEqual(order.order_line.base_price_discount, 10.0)

    def test_sale_price_on_pricelist_pro(self):
        self.env.company.display_base_price_method = "discount_formula"
        order = self.env["sale.order"].create(
            {
                "pricelist_id": self.pricelist_pro.id,
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                        }
                    )
                ],
            }
        )
        self.assertEqual(10.0, order.order_line.base_price)
        self.assertEqual(
            8.1,
            order.order_line.price_unit,
        )
        self.assertTrue(order.order_line.has_discount_price)
        # Check the dubble discount
        self.assertEqual(order.order_line.base_price_discount, 19.0)
