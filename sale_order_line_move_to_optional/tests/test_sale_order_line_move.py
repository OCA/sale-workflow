from odoo.tests import TransactionCase


class TestSaleOrderLineOptional(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test",
            }
        )
        cls.contact = cls.env["res.partner"].create(
            {
                "name": "Contact Test",
                "parent_id": cls.partner.id,
                "type": "contact",
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "service"}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    )
                ],
            }
        )

    def test_order_line_move_to_optional(self):
        """Test moving sale order lines to optional section."""
        optional_model = self.env["sale.order.option"]
        optional_lines = optional_model.search([("order_id", "=", self.order.id)])
        self.assertEqual(len(self.order.order_line), 1)
        self.assertFalse(optional_lines)

        self.order.order_line.move_line_to_optional()
        moved_optional_line = optional_model.search([("order_id", "=", self.order.id)])
        self.assertTrue(moved_optional_line)
