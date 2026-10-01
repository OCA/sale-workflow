# Copyright 2026 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestSaleOrderRounding(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "list_price": 99.37, "taxes_id": False}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product.id, "product_uom_qty": 1}),
                ],
            }
        )

    def test_round_up_adds_line(self):
        self.assertEqual(self.order.amount_total, 99.37)
        self.order.action_apply_round_up()
        rounding_lines = self.order.order_line.filtered("is_rounding_line")
        self.assertEqual(len(rounding_lines), 1)
        self.assertAlmostEqual(rounding_lines.price_unit, 0.63)
        self.assertEqual(self.order.amount_total, 100.0)

    def test_round_up_is_idempotent(self):
        self.order.action_apply_round_up()
        self.order.action_apply_round_up()
        rounding_lines = self.order.order_line.filtered("is_rounding_line")
        self.assertEqual(len(rounding_lines), 1)
        self.assertEqual(self.order.amount_total, 100.0)

    def test_round_up_already_integer(self):
        self.product.list_price = 100.0
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1}),
                ],
            }
        )
        self.assertFalse(order.action_apply_round_up())
        self.assertFalse(order.order_line.filtered("is_rounding_line"))
