# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import freezegun

from odoo import Command

from odoo.addons.sale_order_blanket_order.tests.common import SaleOrderBlanketOrderCase


class TestSaleCallOffOrder(SaleOrderBlanketOrderCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1.standard_price = 10.0

    def test_order_line_margin(self):
        self.blanket_so.action_confirm()
        order = self.env["sale.order"].create(
            {
                "order_type": "call_off",
                "date_order": "2025-02-01",
                "partner_id": self.partner.id,
                "blanket_order_id": self.blanket_so.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 10.0,
                        }
                    ),
                ],
            }
        )
        self.assertRecordValues(
            order.order_line,
            [
                {
                    "margin": 0.0,
                    "margin_percent": 0.0,
                }
            ],
        )
        with freezegun.freeze_time("2025-02-01"):
            order.action_confirm()

        self.assertRecordValues(
            order.order_line,
            [
                {
                    "margin": 0.0,
                    "margin_percent": 0.0,
                }
            ],
        )
