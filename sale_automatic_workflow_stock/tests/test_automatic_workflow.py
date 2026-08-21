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
                # v19: product_category_3 removed; use product_category_services instead
                "categ_id": self.env.ref("product.product_category_services").id,
                "standard_price": 40.0,
                "list_price": 90.0,
                "type": "service",
                "uom_id": self.env.ref("uom.product_uom_hour").id,
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
                        "product_uom_id": product_uom_hour.id,
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

    def test_05_do_validate_picking_bypass(self):
        """Test that _do_validate_picking returns a bypass message when the
        picking no longer matches the domain filter (e.g. already processed)."""
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        # Confirm the order to generate a picking
        sale.action_confirm()
        self.assertTrue(sale.picking_ids)
        picking = sale.picking_ids[0]
        job = self.env["automatic.workflow.job"]
        # Use an impossible filter so the picking is excluded → bypass branch
        result = job._do_validate_picking(picking, [("id", "=", -1)])
        self.assertIn("job bypassed", result)

    def test_06_onchange_workflow_process_id_sets_picking_policy(self):
        """Test that _onchange_workflow_process_id copies picking_policy from
        the workflow to the sale order (covers sale_order.py lines 32-34)."""
        workflow = self.create_full_automatic(override={"picking_policy": "direct"})
        sale = self.create_sale_order(workflow)
        # Manually invoke the onchange (simulates form UI interaction)
        sale._onchange_workflow_process_id()
        self.assertEqual(sale.picking_policy, "direct")

    def test_07_validate_picking_adjusts_partial_move_quantity(self):
        """Test validate_picking when move quantity < product_qty (partial
        stock). Covers stock_picking.py lines 33-34 (inner for loop when
        float_compare(quantity, product_qty) == -1).

        The mixin's create_sale_order auto-stocks exactly line.product_uom_qty
        units, so we bypass it here and create the order/picking directly,
        placing only 1 unit in stock while demanding 2. This ensures the move
        stays partially reserved and the inner adjustment loop is exercised.
        """
        product = self.env["product.product"].create(
            {
                "name": "Partial Stock Product",
                "is_storable": True,
                "list_price": 10.0,
            }
        )
        # Only 1 unit available; demand will be 2.
        quant = self.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "inventory_quantity": 1,
            }
        )
        quant._apply_inventory()

        # Build the sale order directly to skip the mixin's auto-inventory.
        partner = self.env["res.partner"].create({"name": "Test Partner Partial"})
        product_uom_unit = self.env.ref("uom.product_uom_unit")
        sale = (
            self.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": partner.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": product.name,
                                "product_id": product.id,
                                "product_uom_qty": 2,
                                "product_uom_id": product_uom_unit.id,
                            },
                        )
                    ],
                }
            )
        )
        sale.action_confirm()
        picking = sale.picking_ids
        self.assertTrue(picking)

        picking.action_assign()
        # After partial reservation: move.quantity == 1 < move.product_qty == 2
        move = picking.move_ids[0]
        self.assertEqual(move.state, "partially_available")

        # Mark the reserved move-line as picked so the outer filter passes.
        for ml in move.move_line_ids:
            ml.picked = True

        # validate_picking should enter the float_compare == -1 branch and
        # set each move_line.quantity = move_line.quantity_product_uom
        picking.with_context(skip_backorder=True).validate_picking()
        self.assertEqual(picking.state, "done")
