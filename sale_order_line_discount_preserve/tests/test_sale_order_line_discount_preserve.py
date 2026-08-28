from odoo.tests.common import TransactionCase


class TestPreserveDiscount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100.0,
                "standard_price": 50.0,
                "type": "consu",
            }
        )

    def test_discount_is_preserved_on_qty_change(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )

        order_line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "price_unit": self.product.list_price,
                "discount": 20.0,
                "name": self.product.name,
            }
        )

        self.assertEqual(order_line.discount, 20.0, "Initial discount should be 20.0")

        order_line.write({"product_uom_qty": 3})

        self.assertEqual(
            order_line.discount,
            20.0,
            "Discount should be preserved after quantity change",
        )
