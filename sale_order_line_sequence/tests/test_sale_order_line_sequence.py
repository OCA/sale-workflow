# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestSaleOrderLineSequence(TransactionCase):
    def setUp(self):
        super(TestSaleOrderLineSequence, self).setUp()
        self.sale_order = self.env["sale.order"]
        self.sale_order_line = self.env["sale.order.line"]
        self.partner = self.env.ref("base.res_partner_1")
        self.product = self.env.ref("product.product_product_4")

    def test_sale_order_line_sequence(self):
        vals = {
            "partner_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "name": self.product.name,
                        "product_uom_qty": 1.0,
                        "price_unit": self.product.lst_price,
                    },
                )
            ],
        }
        so1 = self.sale_order.create(vals)
        so1.action_confirm()
        self.assertEqual(so1.order_line.sequence, 1)
        so2 = so1.copy()
        self.assertEqual(so2.order_line.sequence, 1)
