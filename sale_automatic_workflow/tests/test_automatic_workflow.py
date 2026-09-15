# Copyright 2014 Camptocamp SA (author: Guewen Baconnier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from unittest import mock

from freezegun import freeze_time

from odoo import fields
from odoo.tests import tagged

from .common import TestAutomaticWorkflowMixin, TestCommon


@tagged("post_install", "-at_install")
class TestAutomaticWorkflow(TestCommon, TestAutomaticWorkflowMixin):
    def setUp(self):
        super().setUp()
        self.env = self.env(
            context=dict(
                self.env.context,
                tracking_disable=True,
                # Compatibility with sale_automatic_workflow_job: even if
                # the module is installed, ensure we don't delay a job.
                # Thus, we test the usual flow.
                queue_job__no_delay=True,
            )
        )

    def test_01_full_automatic(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.workflow_process_id, workflow)
        self.run_job()
        self.assertEqual(sale.state, "sale")
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.state, "posted")

    def test_02_onchange(self):
        team_1 = self.env.ref("sales_team.crm_team_1")
        team_2 = self.env.ref("sales_team.team_sales_department")
        workflow = self.create_full_automatic(override={"team_id": team_1.id})
        sale = self.create_sale_order(workflow)
        self.assertEqual(sale.team_id, team_1)
        workflow2 = self.create_full_automatic(override={"team_id": team_2.id})
        sale.workflow_process_id = workflow2.id
        self.assertEqual(sale.team_id, team_2)

    @freeze_time("2025-1-1")
    def test_03_date_invoice_from_sale_order(self):
        workflow = self.create_full_automatic()
        # date_order on sale.order is date + time
        # invoice_date on account.move is date only
        last_week_time = fields.Datetime.now() - timedelta(days=7)
        override = {"date_order": last_week_time}
        sale = self.create_sale_order(workflow, override=override)
        self.assertEqual(sale.date_order, last_week_time)
        self.run_job()
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.invoice_date, last_week_time.date())
        self.assertEqual(invoice.workflow_process_id, sale.workflow_process_id)

    def test_04_create_invoice_from_sale_order(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        line = sale.order_line[0]
        # Make sure this addon works properly in regards to it.
        mock_path = "odoo.addons.sale.models.sale_order.SaleOrder._create_invoices"
        workflow.invoice_service_delivery = True
        line.qty_delivered_method = "manual"
        with mock.patch(mock_path) as mocked:
            sale._create_invoices()
            mocked.assert_called()
        self.assertEqual(line.qty_delivered, 1.0)

    def test_05_invoice_from_picking_with_service_product(self):
        workflow = self.create_full_automatic()
        product_service = self.env["product.product"].create(
            {
                "name": "Remodeling Service",
                "categ_id": self.env.ref("product.product_category_3").id,
                "standard_price": 40.0,
                "list_price": 90.0,
                "type": "service",
                "uom_id": self.env.ref("uom.product_uom_hour").id,
                "uom_po_id": self.env.ref("uom.product_uom_hour").id,
                "description": "Example of product to invoice on order",
                "default_code": "PRE-PAID",
                "invoice_policy": "order",
            }
        )
        product_uom_hour = self.env.ref("uom.product_uom_hour")
        override = {
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": "Prepaid Consulting",
                        "product_id": product_service.id,
                        "product_uom_qty": 1,
                        "product_uom": product_uom_hour.id,
                    },
                )
            ]
        }
        sale = self.create_sale_order(workflow, override=override)
        self.run_job()
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.workflow_process_id, sale.workflow_process_id)

    def test_06_journal_on_invoice(self):
        sale_journal = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        new_sale_journal = self.env["account.journal"].create(
            {"name": "TTSA", "code": "TTSA", "type": "sale"}
        )

        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        self.run_job()
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.journal_id.id, sale_journal.id)

        workflow = self.create_full_automatic(
            override={"property_journal_id": new_sale_journal.id}
        )
        sale = self.create_sale_order(workflow)
        self.run_job()
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.journal_id.id, new_sale_journal.id)

    def test_filter_domain_with_datetime(self):
        workflow = self.create_full_automatic()
        workflow.order_filter_id = self.env["ir.filters"].create(
            {
                "name": "Order filter using datetime",
                "model_id": "sale.order",
                "domain": (
                    "[('state', '=', 'draft'), "
                    "('date_order', '<=', "
                    "context_today().strftime('%Y-%m-%d %H:%M:%S'))]"
                ),
                "user_id": self.env.ref("base.user_root").id,
            }
        )
        sale = self.create_sale_order(workflow)
        sale.date_order = fields.Datetime.now() + timedelta(days=1)
        self.run_job()
        self.assertEqual(sale.state, "draft")
        sale.date_order = fields.Datetime.now() - timedelta(days=1)
        self.run_job()
        self.assertEqual(sale.state, "sale")

    def test_no_copy(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        self.run_job()
        invoice = sale.invoice_ids
        self.assertTrue(sale.workflow_process_id)
        self.assertTrue(invoice.workflow_process_id)
        sale2 = sale.copy()
        invoice2 = invoice.copy()
        self.assertFalse(sale2.workflow_process_id)
        self.assertFalse(invoice2.workflow_process_id)

    def test_automatic_sale_order_confirmation_mail(self):
        workflow = self.create_full_automatic()
        workflow.send_order_confirmation_mail = True
        sale = self.create_sale_order(workflow)
        previous_message_ids = sale.message_ids
        self.run_job()
        self.assertEqual(sale.state, "sale")
        new_messages = self.env["mail.message"].search(
            [
                ("id", "in", sale.message_ids.ids),
                ("id", "not in", previous_message_ids.ids),
            ]
        )
        self.assertTrue(
            new_messages.filtered(
                lambda x: x.subtype_id == self.env.ref("mail.mt_comment")
            )
        )

    def test_create_payment_with_invoice_currency_id(self):
        workflow = self.create_full_automatic()
        pricelist_id = self.env["product.pricelist"].create(
            {
                "name": "default_pricelist",
                "currency_id": 1,
            }
        )
        product_service = self.env["product.product"].create(
            {
                "name": "Remodeling Service",
                "categ_id": self.env.ref("product.product_category_3").id,
                "standard_price": 40.0,
                "list_price": 90.0,
                "type": "service",
                "uom_id": self.env.ref("uom.product_uom_hour").id,
                "uom_po_id": self.env.ref("uom.product_uom_hour").id,
                "description": "Example of product to invoice on order",
                "default_code": "PRE-PAID",
                "invoice_policy": "order",
            }
        )
        product_uom_hour = self.env.ref("uom.product_uom_hour")
        override = {
            "pricelist_id": pricelist_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": "Prepaid Consulting",
                        "product_id": product_service.id,
                        "product_uom_qty": 1,
                        "product_uom": product_uom_hour.id,
                    },
                )
            ],
        }
        sale = self.create_sale_order(workflow, override=override)
        self.run_job()
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.state, "posted")
        payment_id = self.env["automatic.workflow.job"]._register_payment_invoice(
            invoice
        )
        self.assertTrue(payment_id)
        self.assertEqual(invoice.currency_id.id, payment_id.currency_id.id)
        self.assertEqual(invoice.payment_state, invoice._get_invoice_in_payment_state())

    def test_create_payment_with_specified_payment_journal(self):
        workflow = self.create_full_automatic()
        workflow.register_payment = True
        payment_journal = self.env["account.journal"].create(
            {"name": "Payment Journal Test", "code": "TESTJOURNAL", "type": "bank"}
        )
        workflow.property_payment_journal_id = payment_journal
        self.create_sale_order(workflow)
        self.run_job()
        payment = self.env["account.payment"].search([], limit=1, order="id desc")
        self.assertEqual(payment.journal_id, payment_journal)

    def _create_zero_amount_invoice(self, workflow):
        """Return a posted invoice whose residual amount is zero.

        A free order (100% discount, replacement shipment, loyalty item...)
        produces an invoice with a zero total and therefore a zero residual
        amount.
        """
        sale = self.create_sale_order(
            workflow, extra_product_values={"list_price": 0.0}
        )
        self.run_job()
        invoice = sale.invoice_ids
        self.assertEqual(invoice.state, "posted")
        self.assertTrue(invoice.currency_id.is_zero(invoice.amount_residual))
        return sale, invoice

    def test_register_payment_skips_zero_residual_invoice(self):
        """No payment is created when there is nothing left to pay."""
        workflow = self.create_full_automatic()
        workflow.register_payment = True
        dummy, invoice = self._create_zero_amount_invoice(workflow)
        payment_obj = self.env["account.payment"]
        payments_before = payment_obj.search_count([])
        payment = self.env["automatic.workflow.job"]._register_payment_invoice(invoice)
        self.assertFalse(payment)
        self.assertEqual(payment_obj.search_count([]), payments_before)

    def test_register_payment_zero_residual_invoice_does_not_loop(self):
        """Regression: a zero amount payment never settles the invoice.

        Before this fix, the invoice kept matching the payment filter after
        the payment was created, so every run of the cron added another
        zero amount payment and another posted journal entry, indefinitely.
        """
        workflow = self.create_full_automatic()
        workflow.register_payment = True
        sale, dummy = self._create_zero_amount_invoice(workflow)
        # The partner is created by create_sale_order, so it is only used by
        # this order and we can count its payments safely.
        domain = [("partner_id", "=", sale.partner_id.id)]
        payment_obj = self.env["account.payment"]
        self.assertEqual(payment_obj.search_count(domain), 0)
        for _run in range(3):
            self.run_job()
        self.assertEqual(
            payment_obj.search_count(domain),
            0,
            "A zero amount payment was created for an invoice with nothing "
            "left to pay; the automatic workflow will recreate it on every run.",
        )

    def test_register_payment_is_not_repeated(self):
        """A regular invoice gets exactly one payment, however often we run."""
        workflow = self.create_full_automatic()
        workflow.register_payment = True
        sale = self.create_sale_order(workflow)
        self.run_job()
        invoice = sale.invoice_ids
        self.assertEqual(invoice.state, "posted")
        domain = [("partner_id", "=", sale.partner_id.id)]
        payment_obj = self.env["account.payment"]
        self.assertEqual(payment_obj.search_count(domain), 1)
        self.run_job()
        self.run_job()
        self.assertEqual(payment_obj.search_count(domain), 1)

    def test_do_register_payment_bypassed_when_filter_no_longer_matches(self):
        """The filter is re-checked before acting, like the other actions."""
        workflow = self.create_full_automatic()
        workflow.register_payment = True
        sale = self.create_sale_order(workflow)
        self.run_job()
        invoice = sale.invoice_ids
        job = self.env["automatic.workflow.job"]
        # This invoice is already paid, so it no longer matches the filter.
        result = job._do_register_payment(
            invoice, workflow.payment_filter_id._get_eval_domain()
        )
        self.assertIn("bypassed", result)

    def test_default_payment_filter_excludes_settled_invoices(self):
        payment_filter = self.env.ref(
            "sale_automatic_workflow.automatic_workflow_payment_filter"
        )
        self.assertIn(
            ("amount_residual", "!=", 0),
            payment_filter._get_eval_domain(),
        )
