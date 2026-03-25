# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestSaleLastPriceInfo(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.sale_order_model = self.env["sale.order"]
        self.sale_line_model = self.env["sale.order.line"]
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Customer",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "invoice_policy": "delivery",
            }
        )
        self.sale_order = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

    def test_sale_last_price_info_demo(self):
        self.sale_order.action_confirm()
        sale_line = self.sale_line_model.search(
            [("product_id", "=", self.product.id), ("state", "=", "sale")],
            limit=1,
            order="date_order_sale_last_price_info desc",
        )
        self.assertEqual(
            sale_line.date_order_sale_last_price_info.date(),
            self.product.last_sale_date,
        )
        self.assertEqual(sale_line.price_unit, self.product.last_sale_price)
        self.assertEqual(sale_line.order_id.partner_id, self.product.last_customer_id)
