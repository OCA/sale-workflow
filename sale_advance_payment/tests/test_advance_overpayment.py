# Copyright 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestAdvanceOverpayment(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test data
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "service",
            }
        )

        # Create sale order
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        },
                    ),
                ],
            }
        )

        # Confirm sale order
        cls.sale_order.action_confirm()

        # Get a suitable journal
        cls.journal = cls.env["account.journal"].search(
            [
                ("type", "in", ("bank", "cash")),
                ("company_id", "=", cls.sale_order.company_id.id),
            ],
            limit=1,
        )

    def _create_payment_wizard(self, amount_advance):
        """Helper method to create advance payment wizard"""
        return (
            self.env["account.voucher.wizard"]
            .with_context(
                active_id=self.sale_order.id,
                active_ids=[self.sale_order.id],
            )
            .create(
                {
                    "journal_id": self.journal.id,
                    "amount_advance": amount_advance,
                }
            )
        )

    def test_advance_overpayment_disabled_by_default(self):
        """Test that overpayment is rejected by default in wizard"""
        # Should raise validation error when overpayment is disabled (default)
        # The validation happens during wizard creation due to @api.constrains
        with self.assertRaises(ValidationError) as context:
            self._create_payment_wizard(150.0)  # More than order total
        self.assertIn("greater than residual amount", str(context.exception))

    def test_advance_overpayment_enabled(self):
        """Test that overpayment is allowed when company setting is enabled"""
        # Enable overpayment handling on company
        self.sale_order.company_id.allow_advance_overpayment = True

        # Create advance payment wizard with amount larger than order
        # Should not raise validation error when overpayment is enabled
        try:
            payment_wizard = self._create_payment_wizard(150.0)  # More than order total
        except ValidationError:
            self.fail("raised errorwhen overpayment is enabled")

        # Create the payment
        payment_wizard.make_advance_payment()

        # Verify payment was created
        self.assertTrue(self.sale_order.account_payment_ids)
        payment = self.sale_order.account_payment_ids[0]
        self.assertEqual(payment.amount, 150.0)

        # Create invoice from order
        invoice = self.sale_order._create_invoices()
        invoice.action_post()

        # Verify invoice is fully paid
        self.assertEqual(invoice.payment_state, "paid")

        # Verify there's remaining credit on the payment
        receivable_line = payment.move_id.line_ids.filtered(
            lambda x: x.account_id.account_type == "asset_receivable"
        )[:1]
        self.assertTrue(receivable_line)
        self.assertNotEqual(
            receivable_line.amount_residual_currency
            if receivable_line.currency_id
            else receivable_line.amount_residual,
            0,
        )
