# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestDiscountDisplay(TransactionCase):
    def test_sale_discount_value(self):
        product1 = self.env["product.product"].create(
            {"name": "Product TEST", "type": "consu"}
        )
        customer = self.env["res.partner"].create(
            {"name": "Customer TEST", "is_company": False, "email": "test@tes.ttest"}
        )
        so = self.env["sale.order"].create({"partner_id": customer.id})
        self.env["sale.order.line"].create(
            {"order_id": so.id, "product_id": product1.id, "price_unit": 30.75}
        )

        first_line = so.order_line[0]
        first_line.discount = 10

        self.assertAlmostEqual(first_line.price_subtotal_no_discount, 30.75)
        self.assertAlmostEqual(first_line.price_total_no_discount, 35.36)
        self.assertAlmostEqual(first_line.discount_total, 3.53)
        self.assertAlmostEqual(so.price_subtotal_no_discount, 30.75)
        self.assertAlmostEqual(so.price_total_no_discount, 35.36)
        self.assertAlmostEqual(so.discount_total, 3.53)
