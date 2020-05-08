# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase


class TestSaleFixedDiscount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleFixedDiscount, cls).setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "TAX 15%",
                "amount_type": "percent",
                "type_tax_use": "sale",
                "amount": 15.0,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "consu"}
        )
        cls.sale = cls.env["sale.order"].create(
            {"name": "Test Sale Order", "partner_id": cls.partner.id}
        )
        cls.so_line = cls.env["sale.order.line"]
        cls.sale_line1 = cls.so_line.create(
            {
                "order_id": cls.sale.id,
                "name": "Line 1",
                "price_unit": 200.0,
                "product_uom_qty": 1,
                "product_id": cls.product.id,
                "tax_id": [(6, 0, [cls.tax.id])],
            }
        )

    def test_01_discounts(self):
        """ Tests multiple discounts in line with taxes."""
        # Apply a fixed discount
        self.sale_line1.discount_fixed = 10.0
        self.assertEqual(self.sale.amount_total, 218.50)
        # Try to add also a % discount
        with self.assertRaises(ValidationError):
            self.sale_line1.write({"discount": 50.0})
        # Apply a % discount
        self.sale_line1._onchange_discount_fixed()
        self.sale_line1.discount_fixed = 0.0
        self.sale_line1.discount = 50.0
        self.sale_line1._onchange_discount()
        self.assertEqual(self.sale.amount_total, 115.00)

    def test_02_discounts_multiple_lines(self):
        """ Tests multiple lines with mixed taxes and dicount types."""
        self.sale_line2 = self.so_line.create(
            {
                "order_id": self.sale.id,
                "name": "Line 2",
                "price_unit": 500.0,
                "product_uom_qty": 1,
                "product_id": self.product.id,
                "tax_id": [(5,)],
            }
        )
        self.assertEqual(self.sale_line2.price_subtotal, 500.0)
        # Add a fixed discount
        self.sale_line2.discount_fixed = 100.0
        self.assertEqual(self.sale_line2.price_subtotal, 400.0)
        self.sale._amount_all()
        self.assertEqual(self.sale.amount_total, 630.0)
        self.sale_line1.discount = 50.0
        self.assertEqual(self.sale.amount_total, 515.0)
