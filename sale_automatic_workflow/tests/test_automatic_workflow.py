# Copyright 2014 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools.safe_eval import safe_eval

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
                _job_force_sync=True,
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

    def test_date_invoice_from_sale_order(self):
        workflow = self.create_full_automatic()
        # date_order on sale.order is date + time
        # invoice_date on account.move is date only
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
        with self.assertRaises(UserError):
            sale._create_invoices()
        self.assertEqual(line.qty_delivered, 0.0)
        workflow.invoice_service_delivery = True
        sale.state = "done"
        line.qty_delivered_method = "manual"
        sale._create_invoices()
        self.assertEqual(line.qty_delivered, 1.0)

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
        picking = sale.picking_ids
        self.assertTrue(picking.workflow_process_id)
        picking2 = picking.copy()
        self.assertFalse(picking2.workflow_process_id)

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
        invoice.payment_mode_id = False
        self.assertEqual(invoice.state, "posted")
        payment_id = self.env["automatic.workflow.job"]._register_payment_invoice(
            invoice
        )
        self.assertTrue(payment_id)
        self.assertEqual(invoice.currency_id.id, payment_id.currency_id.id)

    def test_automatic_invoice_send_mail(self):
        def _get_last_sent_messages(invoice, previous_message_ids):
            new_messages = self.env["mail.message"].search(
                [
                    ("id", "in", invoice.message_ids.ids),
                    ("id", "not in", previous_message_ids.ids),
                ]
            )
            return new_messages.filtered(
                lambda x: x.subtype_id == self.env.ref("mail.mt_comment")
            )

        workflow = self.create_full_automatic()
        workflow.send_invoice = False
        sale = self.create_sale_order(workflow)
        sale.user_id = self.user.id
        sale._onchange_workflow_process_id()
        self.run_job()
        invoice = sale.invoice_ids
        invoice.message_subscribe(partner_ids=[invoice.partner_id.id])
        invoice.company_id.invoice_is_email = True

        workflow.send_invoice = True
        sale._onchange_workflow_process_id()
        previous_message_ids = invoice.message_ids
        self.run_job()
        sent_messages = _get_last_sent_messages(invoice, previous_message_ids)
        self.assertTrue(invoice.is_move_sent)
        self.assertTrue(sent_messages)
        msg_body = sent_messages[0].body
        self.assertTrue(
            all(
                s in msg_body for s in [f"{invoice.partner_id.name}", f"{invoice.name}"]
            ),
            "This does not seems to be the default template that was used",
        )

        template = self.env.ref("account.email_template_edi_invoice").copy()
        template.body_html = "This is the body of the test message for Caius Julius"
        workflow.send_invoice_template_id = template
        sale._onchange_workflow_process_id()
        invoice.is_move_sent = False
        previous_message_ids = invoice.message_ids
        self.run_job()
        sent_messages = _get_last_sent_messages(invoice, previous_message_ids)
        self.assertTrue(invoice.is_move_sent)
        self.assertTrue(sent_messages)
        msg_body = sent_messages[0].body
        self.assertIn(
            "This is the body of the test message for Caius Julius",
            msg_body,
            "This does not seems to be the specific template that was used",
        )

    def test_job_bypassing(self):
        """We can only test send_invoice for now as it is the only option
        to actually implement this."""
        workflow = self.create_full_automatic()
        workflow_job = self.env["automatic.workflow.job"]
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        send_invoice_filter = safe_eval(workflow.send_invoice_filter_id.domain)

        # Trigger everything, then check if send invoice jobs is bypassed
        self.run_job()

        invoice = sale.invoice_ids
        res_send_invoice = workflow_job._do_send_invoice(invoice, send_invoice_filter)

        self.assertIn("job bypassed", res_send_invoice)
