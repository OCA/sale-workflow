# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleOrder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrder, cls).setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.product1 = cls.env["product.product"].create({"name": "Test Product 1"})
        cls.product2 = cls.env["product.product"].create({"name": "Test Product 2"})
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "TAX 15%",
                "amount_type": "percent",
                "type_tax_use": "sale",
                "amount": 15.0,
            }
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        so_line = cls.env["sale.order.line"]
        cls.so_line1 = so_line.create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product1.id,
                "name": "Line 1",
                "product_uom_qty": 1.0,
                "tax_id": [(6, 0, [cls.tax.id])],
                "price_unit": 600.0,
            }
        )
        cls.so_line2 = so_line.create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product2.id,
                "name": "Line 2",
                "product_uom_qty": 10.0,
                "tax_id": [(6, 0, [cls.tax.id])],
                "price_unit": 60.0,
            }
        )

    def test_01_sale_order_classic_discount(self):
        """ Tests with single discount """
        self.so_line1.discount = 50.0
        self.so_line2.discount = 75.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 300.0)
        self.assertAlmostEqual(self.so_line2.price_subtotal, 150.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 450.0)
        self.assertAlmostEqual(self.order.amount_tax, 67.5)
        # Mix taxed and untaxed:
        self.so_line1.tax_id = False
        self.assertAlmostEqual(self.order.amount_tax, 22.5)

    def test_02_sale_order_simple_triple_discount(self):
        """ Tests on a single line """
        self.so_line2.unlink()
        # Divide by two on every discount:
        self.so_line1.discount = 50.0
        self.so_line1.discount2 = 50.0
        self.so_line1.discount3 = 50.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 75.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 75.0)
        self.assertAlmostEqual(self.order.amount_tax, 11.25)
        # Unset first discount:
        self.so_line1.discount = 0.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 150.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 150.0)
        self.assertAlmostEqual(self.order.amount_tax, 22.5)
        # Set a charge instead:
        self.so_line1.discount2 = -50.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 450.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 450.0)
        self.assertAlmostEqual(self.order.amount_tax, 67.5)
        # set discount_type to additive
        self.so_line1.discount = 10.0
        self.so_line1.discount2 = 10.0
        self.so_line1.discount3 = 10.0
        self.so_line1.discounting_type = "additive"
        self.assertAlmostEqual(self.so_line1.price_subtotal, 420.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 420.0)
        self.assertAlmostEqual(self.order.amount_tax, 63.0)
        # set discount over 100%
        self.so_line1.discount = 30.0
        self.so_line1.discount2 = 70.0
        self.so_line1.discount3 = 50.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 0.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 0.0)
        self.assertAlmostEqual(self.order.amount_tax, 0.0)

    def test_03_sale_order_complex_triple_discount(self):
        """ Tests on multiple lines """
        self.so_line1.discount = 50.0
        self.so_line1.discount2 = 50.0
        self.so_line1.discount3 = 50.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 75.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 675.0)
        self.assertAlmostEqual(self.order.amount_tax, 101.25)
        self.so_line2.discount3 = 50.0
        self.assertAlmostEqual(self.so_line2.price_subtotal, 300.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 375.0)
        self.assertAlmostEqual(self.order.amount_tax, 56.25)
        self.so_line2.discounting_type = "additive"
        self.so_line2.discount2 = 10.0
        self.assertAlmostEqual(self.so_line2.price_subtotal, 240.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 315.0)
        self.assertAlmostEqual(self.order.amount_tax, 47.25)

    def test_04_sale_order_triple_discount_invoicing(self):
        """ When a confirmed order is invoiced, the resultant invoice
            should inherit the discounts """
        self.so_line1.discount = 50.0
        self.so_line1.discount2 = 50.0
        self.so_line1.discount3 = 50.0
        self.so_line2.discount3 = 50.0
        self.order.action_confirm()
        self.order._create_invoices()
        invoice = self.order.invoice_ids[0]
        self.assertAlmostEqual(
            self.so_line1.discount, invoice.invoice_line_ids[0].discount
        )
        self.assertAlmostEqual(
            self.so_line1.discount2, invoice.invoice_line_ids[0].discount2
        )
        self.assertAlmostEqual(
            self.so_line1.discount3, invoice.invoice_line_ids[0].discount3
        )
        self.assertAlmostEqual(
            self.so_line1.price_subtotal, invoice.invoice_line_ids[0].price_subtotal
        )
        self.assertAlmostEqual(
            self.so_line2.discount3, invoice.invoice_line_ids[1].discount3
        )
        self.assertAlmostEqual(
            self.so_line2.price_subtotal, invoice.invoice_line_ids[1].price_subtotal
        )
        self.assertAlmostEqual(self.order.amount_total, invoice.amount_total)

    def test_05_round_globally(self):
        """ Tests on multiple lines when 'round_globally' is active"""
        self.env.user.company_id.tax_calculation_rounding_method = "round_globally"
        self.so_line1.discount = 50.0
        self.so_line1.discount2 = 50.0
        self.so_line1.discount3 = 50.0
        self.assertEqual(self.so_line1.price_subtotal, 75.0)
        self.assertEqual(self.order.amount_untaxed, 675.0)
        self.assertEqual(self.order.amount_tax, 101.25)
        self.so_line2.discount3 = 50.0
        self.assertEqual(self.so_line2.price_subtotal, 300.0)
        self.assertEqual(self.order.amount_untaxed, 375.0)
        self.assertEqual(self.order.amount_tax, 56.25)
