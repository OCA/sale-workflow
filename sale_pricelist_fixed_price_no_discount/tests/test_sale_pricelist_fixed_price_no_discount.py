# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSalePricelistFixedPriceNoDiscount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product = cls.env["product.product"].create(
            {"name": "Fixed Price Product", "list_price": 100.0}
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Fixed Price Pricelist",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": cls.product.product_tmpl_id.id,
                            "compute_price": "fixed",
                            "fixed_price": 80.0,
                            "base": "list_price",
                        }
                    )
                ],
            }
        )
        cls.order = cls.env["sale.order"].create(
            {"partner_id": cls.partner.id, "pricelist_id": cls.pricelist.id}
        )

    def test_fixed_price_pricelist_rule_sets_technical_boolean(self):
        line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
            }
        )

        self.assertTrue(line.fixed_price_pricelist_rule)

    def test_fixed_price_pricelist_rule_rejects_discount_on_create(self):
        with self.assertRaises(ValidationError):
            self.env["sale.order.line"].create(
                {
                    "order_id": self.order.id,
                    "product_id": self.product.id,
                    "product_uom_qty": 1.0,
                    "discount": 10.0,
                }
            )

    def test_fixed_price_pricelist_rule_rejects_discount_on_write(self):
        line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
            }
        )

        with self.assertRaises(ValidationError):
            line.write({"discount": 10.0})

    def test_fixed_price_pricelist_rule_allows_discount_when_disabled(self):
        self.pricelist.item_ids.fixed_price_no_discount = False
        line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
            }
        )

        self.assertFalse(line.fixed_price_pricelist_rule)
        line.write({"discount": 10.0})
        self.assertEqual(line.discount, 10.0)
