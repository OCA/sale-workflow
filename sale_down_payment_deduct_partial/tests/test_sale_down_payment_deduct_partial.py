# Copyright 2025 ForgeFlow (http://www.forgeflow.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleDownPaymentDeductPartial(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product_1 = cls.env.ref("product.product_product_4")
        cls.product_2 = cls.env.ref("product.product_product_5")
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 1,
                            "price_unit": 1000,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 2,
                            "price_unit": 500,
                        }
                    ),
                ],
            }
        )

        cls.context = {
            "active_model": "sale.order",
            "active_ids": [cls.sale_order.id],
            "active_id": cls.sale_order.id,
        }
        cls.sale_order.action_confirm()
        cls._create_down_payment(cls.sale_order, 100)
        cls._create_down_payment(cls.sale_order, 200)

    @classmethod
    def _create_down_payment(self, sale_order, amount):
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(**self.context)
            .create({"advance_payment_method": "fixed", "fixed_amount": amount})
        )
        inv = wizard._create_invoices(sale_order)
        inv.action_post()
        sale_order.order_line.invalidate_recordset()
        return wizard

    def test_without_down_payment_deduction(self):
        # Check the down payment lines qty_to_invoice remain unchanged
        # After invoicing some products
        dp_lines = self.sale_order.order_line.filtered(
            lambda lin: lin.is_downpayment and not lin.display_type
        )
        for line in dp_lines:
            self.assertEqual(line.qty_to_invoice, -1.0)
        # Deliver the products to be able to invoice
        self.sale_order.order_line.filtered(
            lambda lin: not lin.is_downpayment and not lin.display_type
        )[0].qty_delivered = 1.0
        self.sale_order.order_line.filtered(
            lambda lin: not lin.is_downpayment and not lin.display_type
        )[1].qty_delivered = 2.0
        self.assertEqual(
            self.sale_order.order_line.filtered(
                lambda lin: not lin.is_downpayment and not lin.display_type
            )[0].qty_to_invoice,
            1.0,
        )
        self.assertEqual(
            self.sale_order.order_line.filtered(
                lambda lin: not lin.is_downpayment and not lin.display_type
            )[1].qty_to_invoice,
            2.0,
        )
        # Create invoice without down payment deduction
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(**self.context)
            .create({"deduct_down_payments": False})
        )
        self.assertEqual(wizard.total_deduction_amount, 300)
        self.assertEqual(wizard.deduction_amount, 300)
        # Check the down payment lines qty_to_invoice remain unchanged
        wizard._create_invoices(self.sale_order)
        dp_lines = self.sale_order.order_line.filtered(
            lambda lin: lin.is_downpayment and not lin.display_type
        )
        for line in dp_lines:
            self.assertEqual(line.qty_to_invoice, -1.0)

    def test_full_down_payment_deduction(self):
        # Check the down payment lines qty_to_invoice before invoicing
        dp_lines = self.sale_order.order_line.filtered(
            lambda lin: lin.is_downpayment and not lin.display_type
        )
        for line in dp_lines:
            self.assertEqual(line.qty_to_invoice, -1.0)
            # Deliver some products to be able to invoice
            self.sale_order.order_line.filtered(
                lambda lin: not lin.is_downpayment and not lin.display_type
            )[0].qty_delivered = 1.0
            self.assertEqual(
                self.sale_order.order_line.filtered(
                    lambda lin: not lin.is_downpayment and not lin.display_type
                )[0].qty_to_invoice,
                1.0,
            )
        # Create invoice with full down payment deduction
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(**self.context)
            .create({"down_payment_deduction": "full"})
        )
        self.assertEqual(wizard.total_deduction_amount, 300)
        self.assertEqual(wizard.deduction_amount, 300)
        wizard._create_invoices(self.sale_order)
        # Make sure all down payment lines are fully deducted
        dp_lines = self.sale_order.order_line.filtered(
            lambda lin: lin.is_downpayment and not lin.display_type
        )
        for line in dp_lines:
            self.assertEqual(line.qty_to_invoice, 0.0)

    def test_partial_down_payment_deduction(self):
        # Check the down payment lines qty_to_invoice before invoicing
        # and deliver some products to be able to invoice
        dp_lines = self.sale_order.order_line.filtered(
            lambda lin: lin.is_downpayment and not lin.display_type
        )
        for line in dp_lines:
            self.assertEqual(line.qty_to_invoice, -1.0)
        self.sale_order.order_line.filtered(
            lambda lin: not lin.is_downpayment and not lin.display_type
        )[0].qty_delivered = 1.0

        # Step 1: Deduct 50
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(**self.context)
            .create({"down_payment_deduction": "partial", "deduction_amount": 50})
        )
        self.assertEqual(wizard.total_deduction_amount, 300)
        self.assertEqual(wizard.deduction_amount, 50)
        inv = wizard._create_invoices(self.sale_order)
        inv.action_post()
        self.assertEqual(inv.move_type, "out_invoice")
        self.assertEqual(inv.amount_untaxed, 1000 - 50)
        dp_lines = self.sale_order.order_line.filtered(
            lambda lin: lin.is_downpayment and not lin.display_type
        )
        dp_lines[0].qty_to_invoice = -0.5
        dp_lines[1].qty_to_invoice = -1.0

        # Step 2: Deduct 100 more (total 150)
        self.sale_order.order_line.filtered(
            lambda lin: not lin.is_downpayment and not lin.display_type
        )[1].qty_delivered = 1.0
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(**self.context)
            .create({"down_payment_deduction": "partial", "deduction_amount": 100})
        )
        self.assertEqual(wizard.total_deduction_amount, 250)
        self.assertEqual(wizard.deduction_amount, 100)
        inv = wizard._create_invoices(self.sale_order)
        inv.action_post()
        self.assertEqual(inv.move_type, "out_invoice")
        self.assertEqual(inv.amount_untaxed, 500 - 100)
        dp_lines = self.sale_order.order_line.filtered(
            lambda lin: lin.is_downpayment and not lin.display_type
        )
        dp_lines[0].qty_to_invoice = 0
        dp_lines[1].qty_to_invoice = -0.75

        # Step 3: Deduct 100 more (total 150)
        self.sale_order.order_line.filtered(
            lambda lin: not lin.is_downpayment and not lin.display_type
        )[1].qty_delivered = 2.0
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(**self.context)
            .create({"down_payment_deduction": "partial", "deduction_amount": 50})
        )
        self.assertEqual(wizard.total_deduction_amount, 150)
        self.assertEqual(wizard.deduction_amount, 50)
        inv = wizard._create_invoices(self.sale_order)
        inv.action_post()
        self.assertEqual(inv.move_type, "out_invoice")
        self.assertEqual(inv.amount_untaxed, 500 - 50)
        dp_lines = self.sale_order.order_line.filtered(
            lambda lin: lin.is_downpayment and not lin.display_type
        )
        dp_lines[0].qty_to_invoice = 0
        dp_lines[1].qty_to_invoice = -0.5

        # Step 4: Deduct 100 more (should cap at available, total 300)
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(**self.context)
            .create({"down_payment_deduction": "partial", "deduction_amount": 100})
        )
        self.assertEqual(wizard.total_deduction_amount, 100)
        self.assertEqual(wizard.deduction_amount, 100)
        inv = wizard._create_invoices(self.sale_order)
        inv.action_post()
        self.assertEqual(inv.move_type, "out_refund")
        self.assertEqual(
            inv.amount_untaxed, 100
        )  # Positive amount since it's a credit note
        dp_lines = self.sale_order.order_line.filtered(
            lambda lin: lin.is_downpayment and not lin.display_type
        )
        for line in dp_lines:
            self.assertEqual(line.qty_to_invoice, 0.0)
