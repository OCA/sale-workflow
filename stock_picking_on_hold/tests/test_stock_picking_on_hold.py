# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockPickingOnHoldPaymentMethod(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Use existing manual payment method
        cls.payment_method = cls.env.ref("account.account_payment_method_manual_in")
        cls.payment_method.write(
            {
                "hold_picking_until_payment": True,
            }
        )

        # Use existing bank journal
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )

        # Create payment method line
        cls.payment_method_line = cls.env["account.payment.method.line"].create(
            {
                "name": "Test Payment Method Line",
                "payment_method_id": cls.payment_method.id,
                "journal_id": cls.journal.id,
            }
        )

        # Use existing storable product
        cls.product = cls.env["product.product"].search(
            [("type", "=", "product"), ("invoice_policy", "=", "order")], limit=1
        )

        # Use existing customer
        cls.partner = cls.env["res.partner"].search(
            [("customer_rank", ">", 0)], limit=1
        )

    def test_picking_hold_until_payment(self):
        # Create sale order
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.partner
        sale_form.payment_method_id = self.payment_method
        with sale_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 1
        sale_order = sale_form.save()

        # Confirm sale order
        sale_order.action_confirm()

        # Check that picking doesn't exist yet
        self.assertFalse(
            sale_order.picking_ids,
            "Picking should not exist before payment",
        )

        # Create and post invoice
        sale_order._create_invoices()
        invoice = sale_order.invoice_ids
        invoice.action_post()

        # Register payment
        payment_register = (
            self.env["account.payment.register"]
            .with_context(
                active_model="account.move",
                active_ids=invoice.ids,
            )
            .create(
                {
                    "payment_method_line_id": self.payment_method_line.id,
                    "amount": invoice.amount_total,
                }
            )
        )
        payment_register._create_payments()

        # Check that picking exists
        self.assertTrue(
            sale_order.picking_ids,
            "Picking should exist after payment",
        )

        # Reset payment method configuration
        self.payment_method.write(
            {
                "hold_picking_until_payment": False,
            }
        )


@tagged("post_install", "-at_install")
class TestStockPickingOnHoldCompanySetting(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Set company setting
        cls.company = cls.env.company
        cls.company.write(
            {
                "hold_picking_until_payment": True,
            }
        )

        # Use existing manual payment method
        cls.payment_method = cls.env.ref("account.account_payment_method_manual_in")

        # Use existing bank journal
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )

        # Create payment method line
        cls.payment_method_line = cls.env["account.payment.method.line"].create(
            {
                "name": "Test Payment Method Line",
                "payment_method_id": cls.payment_method.id,
                "journal_id": cls.journal.id,
            }
        )

        # Use existing storable product
        cls.product = cls.env["product.product"].search(
            [("type", "=", "product"), ("invoice_policy", "=", "order")], limit=1
        )

        # Use existing customer
        cls.partner = cls.env["res.partner"].search(
            [("customer_rank", ">", 0)], limit=1
        )

    def test_picking_hold_until_payment(self):
        # Create sale order
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.partner
        with sale_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 1
        sale_order = sale_form.save()

        # Confirm sale order
        sale_order.action_confirm()

        # Check that picking doesn't exist yet
        self.assertFalse(
            sale_order.picking_ids,
            "Picking should not exist before payment",
        )

        # Create and post invoice
        sale_order._create_invoices()
        invoice = sale_order.invoice_ids
        invoice.action_post()

        # Register payment
        payment_register = (
            self.env["account.payment.register"]
            .with_context(
                active_model="account.move",
                active_ids=invoice.ids,
            )
            .create(
                {
                    "payment_method_line_id": self.payment_method_line.id,
                    "amount": invoice.amount_total,
                }
            )
        )
        payment_register._create_payments()

        # Check that picking exists
        self.assertTrue(
            sale_order.picking_ids,
            "Picking should exist after payment",
        )

        # Reset company setting
        self.company.write(
            {
                "hold_picking_until_payment": False,
            }
        )
