# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestSaleAutomaticWorkflowForceInvoiced(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

        product = cls.env.ref("product.product_product_1")

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

        sale_model = cls.env["ir.model"].search([("model", "=", "sale.order")], limit=1)

        filter_record = cls.env["ir.filters"].create(
            {
                "name": "Test Filter Force Invoice",
                "model_id": sale_model.id,
                "domain": "[('id','=',%d)]" % cls.sale_order.id,
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
        job = self.env["automatic.workflow.job"].create({})

        self.sale_order.company_id = self.env.company
        self.other_sale.company_id = self.env.company

        job._force_invoice_orders(
            safe_eval(self.workflow.force_invoice_order_filter_id.domain)
        )

        sale = self.env["sale.order"].browse(self.sale_order.id)
        other = self.env["sale.order"].browse(self.other_sale.id)

        self.assertTrue(
            sale.force_invoiced, "Sale matching filter should be force_invoiced"
        )
        self.assertFalse(
            other.force_invoiced,
            "Sale not matching filter should not be force_invoiced",
        )

    def test_force_invoice_constraint_raises_error(self):
        workflow_model = self.env["sale.workflow.process"]

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

        self.assertIn("Force invoice option is not compatible", str(cm.exception))

    def test_force_invoice_constraint_allows_valid(self):
        workflow_model = self.env["sale.workflow.process"]

        workflow = workflow_model.new(
            {
                "force_invoice": True,
                "create_invoice": False,
                "validate_invoice": False,
                "register_payment": False,
            }
        )

        workflow._check_force_invoice()
