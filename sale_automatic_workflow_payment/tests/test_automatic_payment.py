# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestAutomaticPayment(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self._setup_workflow()
        self._setup_payment_acquirer()
        sale_obj = self.env["sale.order"]
        partner_values = {"name": "Imperator Caius Julius Caesar Divus"}
        partner = self.env["res.partner"].create(partner_values)
        product_values = {"name": "Bread", "list_price": 5, "type": "product"}
        product = self.env["product.product"].create(product_values)
        self.product_uom_unit = self.env.ref("uom.product_uom_unit")
        values = {
            "partner_id": partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom": self.product_uom_unit.id,
                        "price_unit": product.list_price,
                        "product_uom_qty": 1,
                    },
                )
            ],
        }
        self.order = sale_obj.create(values)

    def _setup_payment_acquirer(self):
        vals = {
            "name": "Fake Acquirer",
            "provider": "manual",
            "workflow_process_id": self.workflow.id,
        }
        self.acquirer = self.env["payment.acquirer"].create(vals)

    def _setup_workflow(self):
        workflow_obj = self.env["sale.workflow.process"]
        self.workflow = workflow_obj.create(
            {
                "name": "Full Automatic",
                "picking_policy": "one",
                "validate_order": True,
                "validate_picking": True,
                "create_invoice": True,
                "validate_invoice": True,
                "invoice_date_is_order_date": True,
            }
        )

    def _create_transaction(self, sale):
        vals = {
            "acquirer_id": self.acquirer.id,
            "amount": sale.amount_total,
            "currency_id": sale.currency_id.id,
            "reference": sale.name,
            "sale_order_ids": [(4, self.order.id)],
        }
        self.env["payment.transaction"].create(vals)

    def test_payment_workflow(self):
        # Create a transaction on the Sale Order with the acquirer that
        # references the automatic workflow
        # Check if the workflow is now on Sale Order
        self._create_transaction(self.order)
        self.assertEquals(self.order.workflow_process_id, self.workflow)
