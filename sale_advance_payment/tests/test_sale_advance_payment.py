# Copyright (C) 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

import json

from odoo.tests import common


class TestSaleAdvancePayment(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Partners
        cls.res_partner_1 = cls.env["res.partner"].create({"name": "Wood Corner"})
        cls.res_partner_address_1 = cls.env["res.partner"].create(
            {"name": "Willie Burke", "parent_id": cls.res_partner_1.id}
        )
        cls.res_partner_2 = cls.env["res.partner"].create({"name": "Partner 12"})

        # Products
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Desk Combination", "invoice_policy": "order"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Conference Chair", "invoice_policy": "order"}
        )
        cls.product_3 = cls.env["product.product"].create(
            {"name": "Repair Services", "type": "service", "invoice_policy": "order"}
        )

        cls.tax = cls.env["account.tax"].create(
            {"name": "Tax 15", "type_tax_use": "sale", "amount": 20}
        )

        # Sale Order
        cls.sale_order_1 = cls.env["sale.order"].create(
            {"name": "/", "partner_id": cls.res_partner_1.id}
        )
        cls.order_line_1 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_uom_qty": 10.0,
                "price_unit": 100.0,
                "tax_id": cls.tax,
            }
        )
        cls.order_line_2 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_uom_qty": 25.0,
                "price_unit": 40.0,
                "tax_id": cls.tax,
            }
        )
        cls.order_line_3 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_3.id,
                "product_uom": cls.product_3.uom_id.id,
                "product_uom_qty": 20.0,
                "price_unit": 50.0,
                "tax_id": cls.tax,
            }
        )

        cls.currency_euro = cls.env["res.currency"].search([("name", "=", "EUR")])
        cls.currency_usd = cls.env["res.currency"].search([("name", "=", "USD")])
        cls.currency_rate = cls.env["res.currency.rate"].create(
            {"rate": 1.20, "currency_id": cls.currency_usd.id}
        )

        cls.journal_eur_bank = cls.env["account.journal"].create(
            {
                "name": "Journal Euro Bank",
                "type": "bank",
                "code": "111",
                "currency_id": cls.currency_euro.id,
            }
        )

        cls.journal_usd_bank = cls.env["account.journal"].create(
            {
                "name": "Journal USD Bank",
                "type": "bank",
                "code": "222",
                "currency_id": cls.currency_usd.id,
            }
        )
        cls.journal_eur_cash = cls.env["account.journal"].create(
            {
                "name": "Journal Euro Cash",
                "type": "cash",
                "code": "333",
                "currency_id": cls.currency_euro.id,
            }
        )

        cls.journal_usd_cash = cls.env["account.journal"].create(
            {
                "name": "Journal USD Cash",
                "type": "cash",
                "code": "444",
                "currency_id": cls.currency_usd.id,
            }
        )

    def test_sale_advance_payment(self):
        self.assertEqual(
            self.sale_order_1.amount_residual, 3600,
        )
        self.assertEqual(
            self.sale_order_1.amount_residual,
            self.sale_order_1.amount_total,
            "Amounts should match",
        )

        context_payment = {
            "active_ids": [self.sale_order_1.id],
            "active_id": self.sale_order_1.id,
        }

        # Create Advance Payment 1 - EUR - bank
        advance_payment_1 = (
            self.env["account.voucher.wizard"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_eur_bank.id,
                    "payment_type": "inbound",
                    "amount_advance": 100,
                    "order_id": self.sale_order_1.id,
                }
            )
        )
        advance_payment_1.make_advance_payment()

        self.assertEqual(self.sale_order_1.amount_residual, 3480)

        # Create Advance Payment 2 - USD - cash
        advance_payment_2 = (
            self.env["account.voucher.wizard"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_cash.id,
                    "payment_type": "inbound",
                    "amount_advance": 200,
                    "order_id": self.sale_order_1.id,
                }
            )
        )
        advance_payment_2.make_advance_payment()

        self.assertEqual(self.sale_order_1.amount_residual, 3280)

        # Confirm Sale Order
        self.sale_order_1.action_confirm()

        # Create Advance Payment 3 - EUR - cash
        advance_payment_3 = (
            self.env["account.voucher.wizard"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_eur_cash.id,
                    "payment_type": "inbound",
                    "amount_advance": 250,
                    "order_id": self.sale_order_1.id,
                }
            )
        )
        advance_payment_3.make_advance_payment()
        self.assertEqual(self.sale_order_1.amount_residual, 2980)

        # Create Advance Payment 4 - USD - bank
        advance_payment_4 = (
            self.env["account.voucher.wizard"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_bank.id,
                    "payment_type": "inbound",
                    "amount_advance": 400,
                    "order_id": self.sale_order_1.id,
                }
            )
        )
        advance_payment_4.make_advance_payment()
        self.assertEqual(self.sale_order_1.amount_residual, 2580)

        # Confirm Sale Order
        self.sale_order_1.action_confirm()

        # Create Invoice
        invoice = self.sale_order_1._create_invoices()
        invoice.action_post()

        # Compare payments
        rate = self.currency_rate.rate
        payment_list = [100 * rate, 200, 250 * rate, 400]
        payments = json.loads(invoice.invoice_outstanding_credits_debits_widget)
        result = [d["amount"] for d in payments["content"]]
        self.assertEqual(set(payment_list), set(result))

    def test_sale_advance_payment_outgoing(self):
        self.assertEqual(
            self.sale_order_1.amount_residual, 3600,
        )
        context_payment = {
            "active_ids": [self.sale_order_1.id],
            "active_id": self.sale_order_1.id,
        }
        # Create an inbound payment of 200 USD
        advance_payment_2 = (
            self.env["account.voucher.wizard"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_cash.id,
                    "payment_type": "inbound",
                    "amount_advance": 200,
                    "order_id": self.sale_order_1.id,
                }
            )
        )
        advance_payment_2.make_advance_payment()
        self.assertEqual(self.sale_order_1.amount_residual, 3400)
        # Create an outbound payment of 200 USD
        advance_payment_2 = (
            self.env["account.voucher.wizard"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_cash.id,
                    "payment_type": "outbound",
                    "amount_advance": 200,
                    "order_id": self.sale_order_1.id,
                }
            )
        )
        advance_payment_2.make_advance_payment()
        self.assertEqual(self.sale_order_1.amount_residual, 3600)
