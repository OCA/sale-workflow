# Copyright (C) 2024 Sidoo Soluciones S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
from odoo.tests import common


class TestSalePricelistSaleMargin(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "discount_type": "sale_margin",
                            "sale_margin": 40,
                        },
                    )
                ],
            }
        )

    def test_01_pricelist_margin(self):
        self.assertEqual(self.pricelist.item_ids[0].price_discount, -66.67)
        self.pricelist.item_ids[0].sale_margin = 50
        self.assertEqual(self.pricelist.item_ids[0].price_discount, -100)
