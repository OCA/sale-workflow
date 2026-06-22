# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, new_test_user


class TestSaleInvoiceGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Service",
                "type": "service",
                "invoice_policy": "order",
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product.id, "product_uom_qty": 1})
                ],
            }
        )
        cls.order.action_confirm()
        cls.env.company.restrict_so_invoicing = True

    def _create_invoices_as(self, user):
        self.order.user_id = user
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_user(user)
            .with_context(active_model="sale.order", active_ids=self.order.ids)
            .create({"advance_payment_method": "delivered"})
        )
        return wizard.create_invoices()

    def test_user_without_group_cannot_invoice(self):
        user = new_test_user(
            self.env,
            login="sale_invoice_group_no",
            groups="sales_team.group_sale_salesman",
        )
        with self.assertRaises(AccessError):
            self._create_invoices_as(user)

    def test_user_with_group_can_invoice(self):
        user = new_test_user(
            self.env,
            login="sale_invoice_group_yes",
            groups="sales_team.group_sale_salesman,"
            "sale_invoice_group.group_sale_invoice",
        )
        self._create_invoices_as(user)
        self.assertTrue(self.order.invoice_ids)

    def test_no_restriction_when_disabled(self):
        self.env.company.restrict_so_invoicing = False
        user = new_test_user(
            self.env,
            login="sale_invoice_group_off",
            groups="sales_team.group_sale_salesman",
        )
        self._create_invoices_as(user)
        self.assertTrue(self.order.invoice_ids)
