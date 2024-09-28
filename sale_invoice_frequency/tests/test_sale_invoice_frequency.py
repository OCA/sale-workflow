from odoo.tests.common import TransactionCase


class TestInvoiceFrequency(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create an invoice frequency to use in the test
        self.invoice_frequency = self.env.ref(
            "sale_invoice_frequency.sale_invoice_frequency_monthly"
        )

        # Create a partner with the invoice frequency
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "invoice_frequency_id": self.invoice_frequency.id,
            }
        )

        # Create a sale order
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )

    def test_invoice_frequency_copied_to_sale_order(self):
        """Test if the invoice_frequency_id of res.partner
        is correctly copied to sale.order"""
        self.sale_order._compute_invoice_frequency()
        self.assertEqual(
            self.sale_order.invoice_frequency_id,
            self.partner.invoice_frequency_id,
            "The invoice frequency on the SO should match partner's invoice frequency",
        )

    def test_invoice_frequency_in_commercial_fields(self):
        """Test if the invoice_frequency_id is included in _commercial_fields"""

        # Check if 'invoice_frequency_id' is in the list of commercial fields
        commercial_fields = self.env["res.partner"]._commercial_fields()

        self.assertIn(
            "invoice_frequency_id",
            commercial_fields,
            "The invoice_frequency_id field should included in the commercial fields.",
        )
