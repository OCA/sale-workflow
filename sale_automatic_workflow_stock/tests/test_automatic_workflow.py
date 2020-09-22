# Copyright 2014 Camptocamp SA (author: Guewen Baconnier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.addons.sale_automatic_workflow.tests.common import TestCommon

from .common import TestAutomaticWorkflowStockMixin


class TestAutomaticWorkflow(TestCommon, TestAutomaticWorkflowStockMixin):
    """Test sale automatic workflow with stock."""

    def test_01_full_automatic(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
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

    def test_02_compute_picking_policy(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale.workflow_process_id = workflow.id
        self.assertEqual(sale.picking_policy, "one")
        workflow2 = self.create_full_automatic(override={"picking_policy": "direct"})
        sale.workflow_process_id = workflow2.id
        self.assertEqual(sale.picking_policy, "direct")

    def test_03_create_invoice_from_sale_order(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        line = sale.order_line[0]
        self.assertFalse(workflow.invoice_service_delivery)
        self.assertEqual(line.qty_delivered_method, "stock_move")
        self.assertEqual(line.qty_delivered, 0.0)
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
        # Force the state to "full"
        # note : this is not needed if you have the module sale_delivery_state
        # installed but sale_automatic_workflow do not depend on it
        # so we just force it so we can check the sale.all_qty_delivered
        sale.delivery_status = "full"
        sale._compute_all_qty_delivered()
        self.assertTrue(sale.all_qty_delivered)

    def test_04_invoice_from_picking_with_service_product(self):
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
        self.assertFalse(sale.picking_ids)
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.workflow_process_id, sale.workflow_process_id)
