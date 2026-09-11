# Copyright 2014 Camptocamp SA (author: Guewen Baconnier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import timedelta
from unittest import mock

from freezegun import freeze_time

from odoo import fields
from odoo.tests import tagged
from odoo.tools.safe_eval import safe_eval

from .common import TestAutomaticWorkflowMixin, TestCommon

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install", "mail_composer")
class TestAutomaticWorkflow(TestCommon, TestAutomaticWorkflowMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                queue_job__no_delay=True,
            )
        )

    def test_full_automatic(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.workflow_process_id, workflow)
        self.run_job()
        self.assertEqual(sale.state, "sale")
        self.assertTrue(sale.picking_ids)
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.state, "posted")
        picking = sale.picking_ids
        self.run_job()
        self.assertEqual(picking.state, "done")

    def test_onchange(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        self.assertEqual(sale.picking_policy, "one")
        workflow2 = self.create_full_automatic(override={"picking_policy": "direct"})
        sale.workflow_process_id = workflow2.id
        sale._onchange_workflow_process_id()
        self.assertEqual(sale.picking_policy, "direct")

    @freeze_time("2024-08-11 12:00:00")
    def test_date_invoice_from_sale_order(self):
        workflow = self.create_full_automatic()
        last_week_time = fields.Datetime.now() - timedelta(days=7)
        override = {"date_order": last_week_time}
        sale = self.create_sale_order(workflow, override=override)
        sale._onchange_workflow_process_id()
        self.assertEqual(sale.date_order, last_week_time)
        self.run_job()
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.invoice_date, last_week_time.date())
        self.assertEqual(invoice.workflow_process_id, sale.workflow_process_id)

    def test_create_invoice_from_sale_order(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        line = sale.order_line[0]
        self.assertFalse(workflow.invoice_service_delivery)
        self.assertEqual(line.qty_delivered_method, "stock_move")
        self.assertEqual(line.qty_delivered, 0.0)
        self.assertFalse(sale.delivery_status)
        self.assertFalse(sale.all_qty_delivered)
        mock_path = "odoo.addons.sale.models.sale_order.SaleOrder._create_invoices"
        with mock.patch(mock_path) as mocked:
            sale._create_invoices()
            mocked.assert_called()
        self.assertEqual(line.qty_delivered, 0.0)

        workflow.invoice_service_delivery = True
        line.qty_delivered_method = "manual"
        with mock.patch(mock_path) as mocked:
            sale._create_invoices()
            mocked.assert_called()
        self.assertEqual(line.qty_delivered, 1.0)
        sale.action_confirm()
        sale.delivery_status = "full"
        sale._compute_all_qty_delivered()
        self.assertTrue(sale.all_qty_delivered)

    def test_invoice_from_picking_with_service_product(self):
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
        sale._onchange_workflow_process_id()
        self.run_job()
        self.assertFalse(sale.picking_ids)
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.workflow_process_id, sale.workflow_process_id)

    def test_journal_on_invoice(self):
        sale_journal = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        new_sale_journal = self.env["account.journal"].create(
            {"name": "TTSA", "code": "TTSA", "type": "sale"}
        )
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        self.run_job()
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.journal_id.id, sale_journal.id)

        workflow = self.create_full_automatic(
            override={"property_journal_id": new_sale_journal.id}
        )
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        self.run_job()
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.journal_id.id, new_sale_journal.id)

    def test_automatic_sale_order_confirmation_mail(self):
        workflow = self.create_full_automatic()
        workflow.send_order_confirmation_mail = True
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
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

    def test_automatic_invoice_send_mail(self):
        workflow = self.create_full_automatic()
        workflow.send_invoice = False
        sale = self.create_sale_order(workflow)
        sale.user_id = self.user.id
        sale._onchange_workflow_process_id()
        self.run_job()
        invoice = sale.invoice_ids
        invoice.message_subscribe(partner_ids=[invoice.partner_id.id])
        invoice.company_id.invoice_is_email = True
        previous_message_ids = invoice.message_ids
        workflow.send_invoice = True
        sale._onchange_workflow_process_id()
        self.run_job()
        new_messages = self.env["mail.message"].search(
            [
                ("id", "in", invoice.message_ids.ids),
                ("id", "not in", previous_message_ids.ids),
            ]
        )
        self.assertTrue(
            new_messages.filtered(
                lambda x: x.subtype_id == self.env.ref("mail.mt_comment")
            )
        )

    def test_job_bypassing(self):
        workflow = self.create_full_automatic()
        workflow_job = self.env["automatic.workflow.job"]
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()

        create_invoice_filter = [
            ("state", "in", ["sale", "done"]),
            ("invoice_status", "=", "to invoice"),
            ("workflow_process_id", "=", sale.workflow_process_id.id),
        ]
        order_filter = safe_eval(workflow.order_filter_id.domain)
        validate_invoice_filter = safe_eval(workflow.validate_invoice_filter_id.domain)
        send_invoice_filter = safe_eval(workflow.send_invoice_filter_id.domain)
        self.run_job()
        invoice = sale.invoice_ids
        res_so_validate = workflow_job._do_validate_sale_order(sale, order_filter)
        workflow_job._do_send_order_confirmation_mail(sale)
        res_create_invoice = workflow_job._do_create_invoice(
            sale, create_invoice_filter
        )
        res_validate_invoice = workflow_job._do_validate_invoice(
            invoice, validate_invoice_filter
        )
        res_send_invoice = workflow_job._do_send_invoice(invoice, send_invoice_filter)
        self.assertIn("job bypassed", res_so_validate)
        self.assertTrue(
            "job bypassed" in res_create_invoice or "skipped" in res_create_invoice
        )
        self.assertIn("job bypassed", res_validate_invoice)
        self.assertIn("job bypassed", res_send_invoice)

    def test_do_create_invoice_bypassed_by_domain(self):
        """Invoice creation must be bypassed when the sale order does not match the domain.
        When the domain filter excludes the sale order, _do_create_invoice
        must return a bypassed result without creating any invoice.
        """
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        workflow_job = self.env["automatic.workflow.job"]
        # Use an impossible domain to ensure the sale order is excluded
        domain_filter = [("id", "=", 0)]
        result = workflow_job._do_create_invoice(sale, domain_filter)
        self.assertIn("job bypassed", result)
        self.assertFalse(sale.invoice_ids)

    def test_do_create_invoice_skips_when_posted_invoice_exists(self):
        """Invoice creation must be skipped when a posted invoice already exists.
        When a sale order already has a posted invoice, _do_create_invoice
        must skip the creation to avoid duplicate invoicing.
        """
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        workflow_job = self.env["automatic.workflow.job"]
        # First run: confirm order, create and post the invoice
        self.run_job()
        self.assertTrue(sale.invoice_ids)
        self.assertEqual(len(sale.invoice_ids), 1)
        self.assertEqual(sale.invoice_ids.state, "posted")
        domain_filter = [
            ("state", "in", ["sale", "done"]),
            ("workflow_process_id", "=", sale.workflow_process_id.id),
        ]
        result = workflow_job._do_create_invoice(sale, domain_filter)
        self.assertIn("posted invoice already exists", result)
        # Ensure no new invoice was created
        self.assertEqual(len(sale.invoice_ids), 1)

    def test_do_create_invoice_skips_when_invoice_already_refunded(self):
        """Invoice creation must be skipped when a credit note exists.

        When a posted invoice has been reversed by a credit note (refund),
        _do_create_invoice must skip the creation to avoid re-invoicing.
        """
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        workflow_job = self.env["automatic.workflow.job"]
        # First run: confirm order, create and post the invoice
        self.run_job()
        invoice = sale.invoice_ids
        self.assertTrue(invoice)
        self.assertEqual(invoice.state, "posted")
        # Create a credit note (reversal) for the posted invoice
        refund_wizard = (
            self.env["account.move.reversal"]
            .with_context(
                active_model="account.move",
                active_ids=invoice.ids,
            )
            .create(
                {
                    "reason": "Test refund",
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        refund_wizard.reverse_moves()
        # Search for the credit note instead of relying on res_id
        # (more reliable across different Odoo versions)
        refund = self.env["account.move"].search(
            [
                ("reversed_entry_id", "=", invoice.id),
                ("move_type", "=", "out_refund"),
            ],
            limit=1,
        )
        self.assertTrue(refund, "Credit note was not created")
        if refund.state != "posted":
            refund.action_post()
        domain_filter = [
            ("state", "in", ["sale", "done"]),
            ("workflow_process_id", "=", sale.workflow_process_id.id),
        ]
        result = workflow_job._do_create_invoice(sale, domain_filter)
        self.assertIn("invoice already refunded", result)
        # Credit note is included in invoice_ids, filter for out_invoice only
        out_invoices = sale.invoice_ids.filtered(lambda m: m.move_type == "out_invoice")
        self.assertEqual(len(out_invoices), 1)

    def test_do_create_invoice_success(self):
        """Invoice must be created when no posted invoice exists.
        Disables automatic invoice creation in the workflow to allow
        manual triggering of _do_create_invoice and asserting the result.
        """
        workflow = self.create_full_automatic(
            override={
                "create_invoice": False,
                "validate_invoice": False,
                "send_invoice": False,
            }
        )
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        sale.action_confirm()
        workflow_job = self.env["automatic.workflow.job"]
        domain_filter = [
            ("state", "in", ["sale", "done"]),
            ("workflow_process_id", "=", sale.workflow_process_id.id),
        ]
        self.assertFalse(sale.invoice_ids)
        result = workflow_job._do_create_invoice(sale, domain_filter)
        self.assertIn("create invoice successfully", result)
        self.assertTrue(sale.invoice_ids)
