# Copyright 2014 Camptocamp SA (author: Guewen Baconnier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

import mock

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
        self.assertTrue(sale.delivery_state == "no")
        self.assertFalse(sale.all_qty_delivered)
        # `_create_invoices` is already tested in `sale` module.
        # Make sure this addon works properly in regards to it.
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
        sale.action_force_delivery_state()
        self.assertTrue(sale.delivery_state == "done")
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
