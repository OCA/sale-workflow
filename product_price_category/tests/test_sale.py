# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import Form, TransactionCase


class TestSale(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestSale, cls).setUpClass()
        # activate advanced pricelist
        cls.env.user.write(
            {
                "groups_id": [
                    Command.link(cls.env.ref("product.group_sale_pricelist").id)
                ]
            }
        )
        cls.tax = cls.env["account.tax"].create(
            {"name": "Unittest tax", "amount_type": "percent", "amount": "0"}
        )

        price_category_1 = cls.env["product.price.category"].create(
            {"name": "TEST_CAT"}
        )
        price_category_2 = cls.env["product.price.category"].create(
            {"name": "TEST_CAT_2"}
        )

        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Unittest Pricelist",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "2b_product_price_category",
                            "price_category_id": price_category_2.id,
                            "compute_price": "percentage",
                            "percent_price": 5,
                        }
                    ),
                ],
            }
        )

        # P1 with price_category_1
        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "price_category_id": price_category_1.id,
                "list_price": 10,
                "taxes_id": [Command.set(cls.tax.ids)],
            }
        )

        # P2 with price_category_2
        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Unittest P2",
                "price_category_id": price_category_2.id,
                "list_price": 20,
                "taxes_id": [Command.set(cls.tax.ids)],
            }
        )

        # P3 without price category
        cls.p3 = cls.env["product.product"].create(
            {
                "name": "Unittest P3",
                "list_price": 30,
                "taxes_id": [Command.set(cls.tax.ids)],
            }
        )

        cls.partner = cls.env["res.partner"].create({"name": "Unittest partner"})

        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p1.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                        },
                    ),
                    Command.create(
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p2.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                        },
                    ),
                    Command.create(
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p3.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                        },
                    ),
                ],
            }
        )

    def test_sale_without_pricelist(self):
        self.sale._recompute_prices()
        self.assertEqual(10, self.sale.order_line[0].price_total)
        self.assertEqual(20, self.sale.order_line[1].price_total)
        self.assertEqual(30, self.sale.order_line[2].price_total)
        self.assertEqual(60, self.sale.amount_total)

    def test_sale_with_pricelist(self):
        """Pricelist should be applied only on product with price_category_2"""
        self.sale.pricelist_id = self.pricelist
        self.sale._recompute_prices()
        self.assertEqual(10, self.sale.order_line[0].price_total)
        self.assertEqual(19, self.sale.order_line[1].price_total)
        self.assertEqual(30, self.sale.order_line[2].price_total)
        self.assertEqual(59, self.sale.amount_total)

    def test_sale_with_pricelist_and_tax(self):
        self.tax.amount = 20
        self.sale.pricelist_id = self.pricelist
        self.sale._recompute_prices()
        self.assertEqual(12, self.sale.order_line[0].price_total)
        self.assertEqual(22.8, self.sale.order_line[1].price_total)
        self.assertEqual(36, self.sale.order_line[2].price_total)
        self.assertEqual(70.8, self.sale.amount_total)

    def test_onchange_applied_on_price_category(self):
        pricelist_form = Form(self.pricelist)
        with pricelist_form.item_ids.edit(0) as item_form:
            self.assertTrue(item_form.price_category_id)
            item_form.applied_on = "3_global"
            self.assertFalse(item_form.price_category_id)
