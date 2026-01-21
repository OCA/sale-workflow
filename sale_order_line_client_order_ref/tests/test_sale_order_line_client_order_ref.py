# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestSaleOrderLineClientOrderReference(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.test_product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "service"}
        )
        cls.test_partner = cls.env["res.partner"].create({"name": "Test Partner"})

    def create_sale_order(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.test_partner.id,
                "client_order_ref": "Test Ref",
                "company_id": self.company.id,
            }
        )
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.test_product.id,
                "product_uom_qty": 1.0,
                "price_unit": 100.0,
            }
        )
        return sale_order, order_line

    def test_invoice_line_order_ref(self):
        sale_order, order_line = self.create_sale_order()
        self.assertEqual(order_line.client_order_ref, "Test Ref")
        order_line.write({"client_order_ref": "Test Customer Ref"})
        sale_order.action_confirm()
        invoice = sale_order._create_invoices()
        self.assertEqual(invoice.invoice_line_ids.client_order_ref, "Test Customer Ref")

    def test_invoice_line_description(self):
        sale_order, _ = self.create_sale_order()
        sale_order.action_confirm()
        invoice1 = sale_order._create_invoices()
        self.assertNotIn("Test Ref", invoice1.invoice_line_ids.name)
        invoice1.button_cancel()
        self.company.client_order_ref_in_invoice_line_desc = True
        invoice2 = sale_order._create_invoices()
        self.assertIn("Test Ref", invoice2.invoice_line_ids.name)

    def test_so_line_client_ref_policy(self):
        self.company.so_line_client_ref_policy = "never"
        sale_order, order_line = self.create_sale_order()
        self.assertFalse(order_line.client_order_ref)
        self.company.so_line_client_ref_policy = "sync"
        sale_order, order_line = self.create_sale_order()
        self.assertEqual(order_line.client_order_ref, "Test Ref")
        # Test partner-specific policy
        self.company.so_line_client_ref_policy = "sync"
        self.test_partner.so_line_client_ref_policy = "never"
        sale_order, order_line = self.create_sale_order()
        self.assertFalse(order_line.client_order_ref)
        self.company.so_line_client_ref_policy = "never"
        self.test_partner.so_line_client_ref_policy = "sync"
        sale_order, order_line = self.create_sale_order()
        sale_order.client_order_ref = "Ref"
        self.assertEqual(order_line.client_order_ref, "Ref")
