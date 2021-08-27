# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import SavepointCase


class TestSaleException(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.exception = cls.env.ref(
            "sale_product_brand_exception.exception_product_brand_mixed"
        )
        cls.exception.active = True

        partner_order = cls.env.ref("base.res_partner_1")
        product_1 = cls.env.ref("product.product_product_6")
        product_2 = cls.env.ref("product.product_product_7")

        cls.product_brand1 = cls.env["product.brand"].create(
            {
                "name": "Test Brand 1",
            }
        )
        cls.product_brand2 = cls.env["product.brand"].create(
            {
                "name": "Test Brand 2",
            }
        )
        product_1.product_brand_id = cls.product_brand1
        product_2.product_brand_id = cls.product_brand2

        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": partner_order.id,
                "partner_invoice_id": partner_order.id,
                "partner_shipping_id": partner_order.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product_1.name,
                            "product_id": product_1.id,
                            "product_uom_qty": 1,
                            "product_uom": product_1.uom_id.id,
                            "price_unit": 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": product_2.name,
                            "product_id": product_2.id,
                            "product_uom_qty": 1,
                            "product_uom": product_2.uom_id.id,
                            "price_unit": 1,
                        },
                    ),
                ],
            }
        )

    def test_cannot_mix1(self):
        self.sale.action_confirm()
        self.assertEqual(self.sale.state, "draft")
        self.assertEqual(len(self.sale.exception_ids), 1)
        self.assertEqual(self.sale.exception_ids[0], self.exception)

    def test_cannot_mix2(self):
        self.product_brand1.sale_order_mixed = True
        self.sale.action_confirm()
        self.assertEqual(self.sale.state, "draft")
        self.assertEqual(len(self.sale.exception_ids), 1)
        self.assertEqual(self.sale.exception_ids[0], self.exception)

    def test_can_mix(self):
        self.product_brand1.sale_order_mixed = True
        self.product_brand2.sale_order_mixed = True
        self.sale.action_confirm()
        self.assertEqual(self.sale.state, "sale")
        self.assertEqual(len(self.sale.exception_ids), 0)
