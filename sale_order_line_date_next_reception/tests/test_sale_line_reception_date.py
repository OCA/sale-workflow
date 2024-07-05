# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase


class TestSaleLineReceptionDate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_12")
        self.product_id = self.env.ref("product.product_product_5")

        self.purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "date_order": datetime.today() + relativedelta(days=10),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id.id,
                            "product_qty": 5,
                        },
                    )
                ],
            }
        )

    def test_date_next_reception(self):
        self.purchase_order.button_confirm()
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_id.id, "product_uom_qty": 2})
                ],
            }
        )
        self.assertEqual(
            self.purchase_order.date_planned.date(),
            self.sale_order.order_line.date_next_reception,
        )

    def test_2_date_next_reception(self):
        self.purchase_order.button_confirm()
        self.purchase_order2 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "date_order": datetime.today() + relativedelta(days=4),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id.id,
                            "product_qty": 5,
                        },
                    )
                ],
            }
        )
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_id.id, "product_uom_qty": 2})
                ],
            }
        )
        self.purchase_order2.button_confirm()
        self.assertEqual(
            self.purchase_order2.date_planned.date(),
            self.sale_order.order_line.date_next_reception,
        )
