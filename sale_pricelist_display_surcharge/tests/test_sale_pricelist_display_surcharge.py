# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import common


class TestModule(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Tax",
                "amount": "0.00",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "default_code": "pricelist-margin-product",
                "name": "Demo Product (Margin per Pricelist module)",
                "list_price": 50,
                "taxes_id": cls.tax,
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "percentage",
                            "percent_price": -10.0,
                            "date_start": fields.Datetime.now(),
                            "product_tmpl_id": cls.product.product_tmpl_id.id,
                            "show_surcharge": False,
                        },
                    )
                ],
            }
        )

    def test_01_surcharge_computation(self):
        sale_order = self.env["sale.order"].create(
            {
                "name": "Sale order",
                "partner_id": self.env.user.partner_id.id,
                "pricelist_id": self.pricelist.id,
            }
        )
        line = self.env["sale.order.line"].create(
            {
                "name": "Sale order",
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 10,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.assertEqual(line.discount, 0.0)
        self.assertEqual(line.price_unit, 55.0)
        self.assertEqual(line.price_subtotal, 550.0)

        self.pricelist.item_ids.show_surcharge = True

        sale_order = self.env["sale.order"].create(
            {
                "name": "Sale order",
                "partner_id": self.env.user.partner_id.id,
                "pricelist_id": self.pricelist.id,
            }
        )
        line = self.env["sale.order.line"].create(
            {
                "name": "Sale order",
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 10,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.assertEqual(line.discount, -10.0)
        self.assertEqual(line.price_unit, 50.0)
        self.assertEqual(line.price_subtotal, 550.0)
