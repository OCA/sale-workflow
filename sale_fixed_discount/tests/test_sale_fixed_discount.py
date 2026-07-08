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
        """Test discount_fixed value propagation to account.move.
        Case of editing order line by using UI.
        """
        with Form(self.sale) as sale_order:
            with sale_order.order_line.edit(0) as line:
                line.discount_fixed = 20.0

        self.sale.action_confirm()
        self.sale._create_invoices()

        self.assertEqual(self.sale.invoice_ids.invoice_line_ids.discount_fixed, 20.0)
        self.assertEqual(self.sale.invoice_ids.invoice_line_ids.discount, 10.0)

        self.assertEqual(self.sale.invoice_ids.tax_totals["amount_untaxed"], 180.0)
        self.assertEqual(self.sale.invoice_ids.tax_totals["amount_total"], 207.0)

    def test_06_downpayment_price_included_tax(self):
        """A fixed-amount down payment on an order taxed with a price-included
        tax must produce a consistent tax breakdown.

        Regression test: the ``_convert_to_tax_base_line_dict`` override used to
        drop the ``**kwargs`` (notably ``handle_price_include=False``) forwarded
        by the down payment wizard for lines without a fixed discount. As a
        result the down payment base was computed as tax-included, and the
        invoice ended up with an inconsistent tax amount (base 68.31 / tax 31.69
        instead of base 82.64 / tax 17.36 for a 100.0 down payment).
        """
        tax_incl = self.env["account.tax"].create(
            {
                "name": "TAX 21% incl",
                "amount_type": "percent",
                "type_tax_use": "sale",
                "amount": 21.0,
                "price_include": True,
                "include_base_amount": False,
            }
        )
        order = self.env["sale.order"].create(
            {"name": "DP Order", "partner_id": self.partner.id}
        )
        # Build the line through a Form so that price_unit is set last and is
        # not overwritten by the pricelist-based _compute_price_unit.
        with Form(order) as order_form:
            with order_form.order_line.new() as line:
                line.product_id = self.product
                line.product_uom_qty = 1
                line.tax_id.clear()
                line.tax_id.add(tax_incl)
                line.price_unit = 1000.0

        # Sanity check: the price-included tax splits 1000 into 826.45 + 173.55.
        self.assertAlmostEqual(order.amount_untaxed, 826.45, places=2)
        self.assertAlmostEqual(order.amount_total, 1000.0, places=2)

        order.action_confirm()
        wizard = self.env["sale.advance.payment.inv"].create(
            {
                "advance_payment_method": "fixed",
                "fixed_amount": 100.0,
                "sale_order_ids": [(6, 0, order.ids)],
            }
        )
        wizard.create_invoices()
        invoice = order.invoice_ids
        self.assertEqual(len(invoice), 1)
        # The total must be the requested 100.0, split coherently at 21%.
        self.assertAlmostEqual(invoice.amount_total, 100.0, places=2)
        self.assertAlmostEqual(invoice.amount_untaxed, 82.64, places=2)
        self.assertAlmostEqual(invoice.amount_tax, 17.36, places=2)

    def test_04_fixed_discount_without_price(self):
        with Form(self.sale) as sale_order:
            with sale_order.order_line.edit(0) as line:
                line.product_uom_qty = 1.0
                line.price_unit = 0.0
                line.discount_fixed = 50.0
                self.assertEqual(line.discount, 0.0)
                self.assertEqual(line.price_subtotal, 0.0)
        self.assertEqual(self.sale.amount_total, 0.0)

    def test_05_fixed_discount_invoice(self):
        """Test discount_fixed value propagation to account.move.
        Case of editing order line without using UI (onchange would be not triggered).
        """
        self.sale.order_line.discount_fixed = 20.0

        self.sale.action_confirm()
        self.sale._create_invoices()

        self.assertEqual(self.sale.invoice_ids.invoice_line_ids.discount_fixed, 20.0)
        self.assertEqual(self.sale.invoice_ids.invoice_line_ids.discount, 10.0)

        self.assertEqual(self.sale.invoice_ids.tax_totals["amount_untaxed"], 180.0)
        self.assertEqual(self.sale.invoice_ids.tax_totals["amount_total"], 207.0)
