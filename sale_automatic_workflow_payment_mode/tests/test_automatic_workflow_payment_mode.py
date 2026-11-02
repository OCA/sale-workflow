# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo import fields

from odoo.addons.account.models.account_payment_method import AccountPaymentMethod
from odoo.addons.sale_automatic_workflow.tests.common import (
    TestAutomaticWorkflowMixin,
    TestCommon,
)


class TestAutomaticWorkflowPaymentMode(TestCommon, TestAutomaticWorkflowMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                # Compatibility with sale_automatic_workflow_job: even if
                # the module is installed, ensure we don't delay a job.
                # Thus, we test the usual flow.
                _job_force_sync=True,
            )
        )

    def setUp(self):
        super(TestAutomaticWorkflowPaymentMode, self).setUp()
        Method_get_payment_method_information = (
            AccountPaymentMethod._get_payment_method_information
        )

        def _get_payment_method_information(self):
            res = Method_get_payment_method_information(self)
            res["definb"] = {"mode": "multi", "domain": [("type", "=", "bank")]}
            return res

        with patch.object(
            AccountPaymentMethod,
            "_get_payment_method_information",
            _get_payment_method_information,
        ):
            self.pay_method = self.env["account.payment.method"].create(
                {"name": "default inbound", "code": "definb", "payment_type": "inbound"}
            )

    def create_sale_order(self, workflow, override=None):
        new_order = super().create_sale_order(workflow, override)
        return new_order

    def create_full_automatic(self, override=None):
        workflow = super().create_full_automatic(override)
        reg_pay_dict = {"register_payment": True}
        workflow.update(reg_pay_dict)

        self.acc_journ = self.env["account.journal"].create(
            {"name": "Bank US", "type": "bank", "code": "BNK68"}
        )
        self.pay_mode = self.env["account.payment.mode"].create(
            {
                "name": "Julius Caesare payment",
                "bank_account_link": "fixed",
                "fixed_journal_id": self.acc_journ.id,
                "payment_method_id": self.pay_method.id,
                "workflow_process_id": workflow.id,
            }
        )
        return workflow

    def test_full_automatic(self):
        workflow = self.create_full_automatic()
        self.pay_mode.write(
            {
                "bank_account_link": "variable",
                "fixed_journal_id": False,
            }
        )
        sale = self.create_sale_order(workflow)
        sale.payment_mode_id = self.pay_mode
        sale._onchange_workflow_process_id()

        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.workflow_process_id, workflow)
        self.env["automatic.workflow.job"].run()
        self.assertEqual(sale.state, "sale")
        self.assertTrue(sale.picking_ids)
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.payment_state, "not_paid")

        self.pay_mode.write(
            {
                "bank_account_link": "fixed",
                "fixed_journal_id": self.acc_journ,
            }
        )
        self.env["automatic.workflow.job"].run()
        self.assertEqual(invoice.payment_state, "paid")
        picking = sale.picking_ids
        self.assertEqual(picking.state, "done")

    def _create_foreign_invoice(self):
        currency = self.env.ref(
            "base.USD" if self.env.company.currency_id.name == "EUR" else "base.EUR"
        )
        currency.active = True
        self.env["res.currency.rate"].search(
            [
                ("currency_id", "=", currency.id),
                ("name", "=", fields.Date.today()),
                ("company_id", "=", self.env.company.id),
            ]
        ).unlink()
        self.env["res.currency.rate"].create(
            {
                "currency_id": currency.id,
                "name": fields.Date.today(),
                "rate": 2.0,
                "company_id": self.env.company.id,
            }
        )
        partner = self.env["res.partner"].create({"name": "Currency partner"})
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "currency_id": currency.id,
                "invoice_date": fields.Date.today(),
                "payment_mode_id": self.pay_mode.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Bread",
                            "quantity": 1,
                            "price_unit": 100.0,
                            "tax_ids": [(5, 0, 0)],
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        return invoice

    def _find_payment(self, last_payment_id):
        payment = self.env["account.payment"].search(
            [("id", ">", last_payment_id)], order="id desc", limit=1
        )
        self.assertTrue(payment, "No payment was created")
        return payment

    def _last_payment_id(self):
        payment = self.env["account.payment"].search([], order="id desc", limit=1)
        return payment.id or 0

    def test_04_payment_mode_submodule_preserves_currency(self):
        self.create_full_automatic()
        invoice = self._create_foreign_invoice()
        self.assertNotEqual(invoice.currency_id, self.env.company.currency_id)
        last_payment_id = self._last_payment_id()
        self.env["automatic.workflow.job"]._register_payment_invoice(invoice)
        payment = self._find_payment(last_payment_id)
        self.assertEqual(payment.journal_id, self.acc_journ)
        self.assertEqual(
            payment.currency_id,
            invoice.currency_id,
            "Payment currency must match the invoice currency",
        )

    def test_05_fixed_journal_with_own_currency(self):
        self.create_full_automatic()
        company_currency = self.env.company.currency_id
        self.acc_journ.currency_id = company_currency
        invoice = self._create_foreign_invoice()
        self.assertNotEqual(invoice.currency_id, company_currency)
        last_payment_id = self._last_payment_id()
        self.env["automatic.workflow.job"]._register_payment_invoice(invoice)
        payment = self._find_payment(last_payment_id)
        self.assertEqual(payment.journal_id, self.acc_journ)
        self.assertEqual(payment.currency_id, invoice.currency_id)
        self.assertIn(invoice.payment_state, ("paid", "in_payment"))
