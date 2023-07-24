# Copyright 2017-18 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase


class TestSaleFixedDiscount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("product.group_discount_per_so_line")
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
        cls.product2 = cls.env["product.product"].create(
            {"name": "Test product 2", "type": "consu"}
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
        """Tests multiple discounts in line with taxes."""
        with Form(self.sale) as sale_order:
            with sale_order.order_line.edit(0) as line:
                line.discount_fixed = 20.0
                self.assertEqual(line.discount, 10.0)
                self.assertEqual(line.price_subtotal, 180.0)

        self.assertEqual(self.sale.amount_total, 207.00)

        with Form(self.sale) as sale_order:
            with sale_order.order_line.edit(0) as line:
                line.product_uom_qty = 2
                line.price_unit = 200.0
                self.assertEqual(line.discount, 10.0)
                self.assertEqual(line.price_subtotal, 360.0)

        self.assertEqual(self.sale.amount_total, 414.00)

        with Form(self.sale) as sale_order:
            with sale_order.order_line.edit(0) as line:
                line.product_uom_qty = 1
                line.price_unit = 200.0
                line.discount_fixed = 0.0
                line.discount = 50.0
                self.assertEqual(line.price_subtotal, 100.0)

        self.assertEqual(self.sale.amount_total, 115.00)

        with Form(self.sale) as sale_order:
            with sale_order.order_line.new() as line2:
                line2.product_id = self.product2
                line2.product_uom_qty = 1
                line2.price_unit = 100.0
                line2.discount_fixed = 5.0
                self.assertEqual(line2.discount, 5.0)
                self.assertEqual(line2.price_subtotal, 95.0)

        #
        self.assertEqual(self.sale.amount_total, 224.25)

    def test_02_fixed_discount_mismatch(self):
        """Tests fixed discount mismatch."""
        with self.assertRaisesRegex(
            ValidationError,
            "Please correct one of the discounts",
        ):
            with Form(self.sale) as sale_order:
                with sale_order.order_line.edit(0) as line:
                    line.discount_fixed = 20.0
                    line.discount = 5.0

    def test_03_fixed_discount_invoice(self):
        """Test discount_fixed value propagation to account.move"""
        with Form(self.sale) as sale_order:
            with sale_order.order_line.edit(0) as line:
                line.discount_fixed = 20.0

        self.sale.action_confirm()
        self.sale._create_invoices()

        self.assertEqual(self.sale.invoice_ids.invoice_line_ids.discount_fixed, 20.0)
