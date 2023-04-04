# Copyright 2023 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestSalePurchaseRequisitionAnalytic(TransactionCase):
    def setUp(self):
        super().setUp()
        self.products = self.env["product.product"].create(
            [
                {
                    "name": "Product A",
                    "default_code": "PA",
                    "lst_price": 100.0,
                    "standard_price": 100.0,
                },
                {
                    "name": "Product B",
                    "default_code": "PB",
                    "lst_price": 50.0,
                    "standard_price": 50.0,
                },
            ]
        )

        self.analytic_account_test = self.env["account.analytic.account"].create(
            {"name": "Test Account"}
        )
        self.customer = self.env["res.partner"].create(
            {
                "name": "test customer",
            }
        )

    def test_create_purchase_requisition(self):
        # User creates a sale order
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.customer
        so_form.analytic_account_id = self.analytic_account_test
        with so_form.order_line.new() as line_form:
            line_form.product_id = self.products[0]
            line_form.product_uom_qty = 10
        so = so_form.save()
        # User creates the related purchase requisition
        action = so.action_create_purchase_requisition()
        self.assertFalse("res_id" in action)
        pr_form = Form(self.env[action["res_model"]].with_context(action["context"]))
        pr = pr_form.save()
        self.assertFalse(not pr.analytic_account_id)
