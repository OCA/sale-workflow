# Copyright 2023 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import tagged
from odoo.tests.common import Form

from odoo.addons.sale_invoice_plan.tests.test_sale_invoice_plan import (
    TestSaleInvoicePlan,
)


@tagged("post_install", "-at_install")
class TestSaleInvoicePlanRetention(TestSaleInvoicePlan):
    def setUp(self):
        super().setUp()

    def test_invoice_plan_retention(self):
        # To create next invoice from SO
        ctx = {
            "active_id": self.so_service.id,
            "active_ids": [self.so_service.id],
            "all_remain_invoices": False,
        }

        # Create Invoice Plan 5 installment
        with Form(self.env["sale.create.invoice.plan"]) as f:
            f.num_installment = 5
        plan = f.save()
        plan.with_context(**ctx).sale_create_invoice_plan()
        # Change plan, so that the 1st installment is 1000 and 5th is 3000
        self.assertEqual(len(self.so_service.invoice_plan_ids), 5)
        self.so_service.payment_retention = "amount"
        self.so_service.amount_retention = 20.0
        # Confirm the SO
        self.so_service.action_confirm()
        # Create one invoice
        make_wizard = self.env["sale.make.planned.invoice"].create({})
        make_wizard.with_context(**ctx).create_invoices_by_plan()
        self.assertEqual(
            self.so_service.invoice_plan_ids[0].amount,
            sum(self.so_service.invoice_ids.mapped("amount_total")),
        )
        invoices = self.so_service.invoice_ids
        self.assertEqual(len(invoices), 1)
        # Check invoices has retention following purchase
        self.assertEqual(
            list(set(self.so_service.invoice_ids.mapped("payment_retention"))),
            ["amount"],
        )
        self.assertEqual(
            list(set(self.so_service.invoice_ids.mapped("amount_retention"))),
            [20.0],
        )
