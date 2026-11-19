# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSaleAutomaticWorkflowForceInvoiced(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

        product = cls.env["product.product"].create({"name": "Test Product"})

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )

        cls.other_sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1,
                            "price_unit": 20,
                        },
                    )
                ],
            }
        )

        filter_record = cls.env["ir.filters"].create(
            {
                "name": "Test Filter Force Invoice",
                "model_id": "sale.order",
                "domain": f"[('id','=',{cls.sale_order.id})]",
            }
        )

        cls.workflow = cls.env["sale.workflow.process"].create(
            {
                "name": "Test Workflow Force Invoice",
                "force_invoice": True,
                "force_invoice_order_filter_id": filter_record.id,
            }
        )

    def test_do_force_invoice_orders(self):
        job = self.env["automatic.workflow.job"].create({})

        self.assertFalse(self.sale_order.force_invoiced)

        job._do_force_invoice_orders(self.sale_order)

        sale = self.env["sale.order"].browse(self.sale_order.id)
        self.assertTrue(sale.force_invoiced)

    def test_force_invoice_orders(self):
        job = self.env["automatic.workflow.job"].create({})

        self.assertFalse(self.sale_order.force_invoiced)
        self.assertFalse(self.other_sale.force_invoiced)

        order_filter = [("id", "=", self.sale_order.id)]
        job._force_invoice_orders(order_filter)

        sale = self.env["sale.order"].browse(self.sale_order.id)
        other = self.env["sale.order"].browse(self.other_sale.id)

        self.assertTrue(sale.force_invoiced)
        self.assertFalse(other.force_invoiced)

    def test_run_with_workflow(self):
        """Test that run_with_workflow triggers force invoice correctly.
        It should only trigger on orders matching the workflow domain.
        """
        job = self.env["automatic.workflow.job"].create({})

        # Assign workflow to sale order
        self.sale_order.workflow_process_id = self.workflow.id

        self.sale_order.company_id = self.env.company
        self.other_sale.company_id = self.env.company

        # Call the actual run_with_workflow method instead of
        # _force_invoice_orders directly to cover the method logic
        job.run_with_workflow(self.workflow)

        sale = self.env["sale.order"].browse(self.sale_order.id)
        other = self.env["sale.order"].browse(self.other_sale.id)

        self.assertTrue(
            sale.force_invoiced, "Sale matching filter should be force_invoiced"
        )
        self.assertFalse(
            other.force_invoiced,
            "Sale not matching filter should not be force_invoiced",
        )

    def test_force_invoice_orders_exception(self):
        """Test that exceptions in _do_force_invoice_orders are caught and logged."""
        job = self.env["automatic.workflow.job"].create({})

        # We patch _do_force_invoice_orders to raise an Exception
        from unittest.mock import patch

        with patch.object(
            type(job), "_do_force_invoice_orders", side_effect=Exception("Test Error")
        ):
            order_filter = [("id", "=", self.sale_order.id)]
            # It should not raise an exception, but catch and log it
            job._force_invoice_orders(order_filter)

        # The force_invoiced should remain False as it crashed
        self.assertFalse(self.sale_order.force_invoiced)

    def test_force_invoice_constraint_raises_error(self):
        """Test that force_invoice cannot be combined with create_invoice,
        validate_invoice, or register_payment.
        """
        workflow_model = self.env["sale.workflow.process"]

        # Test combination with create_invoice
        workflow = workflow_model.new(
            {
                "force_invoice": True,
                "create_invoice": True,
                "validate_invoice": False,
                "register_payment": False,
            }
        )

        with self.assertRaises(ValidationError) as cm:
            workflow._check_force_invoice()

        self.assertIn(
            "Force invoice option is not compatible with: Create Invoice",
            str(cm.exception),
        )

        # Test combination with validate_invoice
        workflow = workflow_model.new(
            {
                "force_invoice": True,
                "create_invoice": False,
                "validate_invoice": True,
                "register_payment": False,
            }
        )

        with self.assertRaises(ValidationError) as cm:
            workflow._check_force_invoice()

        self.assertIn(
            "Force invoice option is not compatible with: Validate Invoice",
            str(cm.exception),
        )

        # Test combination with register_payment
        workflow = workflow_model.new(
            {
                "force_invoice": True,
                "create_invoice": False,
                "validate_invoice": False,
                "register_payment": True,
            }
        )

        with self.assertRaises(ValidationError) as cm:
            workflow._check_force_invoice()

        self.assertIn(
            "Force invoice option is not compatible with: Register Payment",
            str(cm.exception),
        )

    def test_force_invoice_constraint_allows_valid(self):
        """Test that force_invoice alone does not raise any constraint error."""
        workflow_model = self.env["sale.workflow.process"]

        workflow = workflow_model.new(
            {
                "force_invoice": True,
                "create_invoice": False,
                "validate_invoice": False,
                "register_payment": False,
            }
        )

        # Should not raise any error
        workflow._check_force_invoice()
