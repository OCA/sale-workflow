# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests import Form, common, new_test_user, users


class SaleOrderForceInvoiceability(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.products = cls.env["product.product"].create(
            {"name": "test product 1", "invoice_policy": "order"}
        )
        cls.products |= cls.env["product.product"].create(
            {"name": "test product 2", "invoice_policy": "delivery"}
        )
        new_test_user(
            cls.env,
            login="test-sale-user",
            groups="sales_team.group_sale_salesman_all_leads",
        )
        new_test_user(
            cls.env,
            login="test-sale-manager",
            groups="sales_team.group_sale_manager",
        )
        sale = Form(cls.env["sale.order"])
        sale.partner_id = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        for product in cls.products:
            with sale.order_line.new() as order_line:
                order_line.product_id = product
                order_line.product_uom_qty = 5
        cls.sale_order = sale.save()

    @users("admin", "test-sale-manager")
    def test_01_force_invoiceability_draft(self):
        """Try to force invoiceability"""
        # The order is still not in `sale` mode so we can't force it
        self.sale_order = self.env["sale.order"].browse(self.sale_order.id)
        with self.assertRaises(UserError) as cm:
            self.sale_order.force_lines_to_invoice_policy_order()
        self.assertEqual(
            "You can't perform this action over a sale order in this state",
            cm.exception.args[0],
        )

    @users("test-sale-user")
    def test_02_force_invoiceability_no_permissions(self):
        # Only users with sales manager permission can force the lines
        self.sale_order = self.env["sale.order"].browse(self.sale_order.id)
        self.sale_order.action_confirm()
        with self.assertRaises(UserError) as cm:
            self.sale_order.force_lines_to_invoice_policy_order()
        self.assertEqual(
            "Only Sales Managers are allowed to force the lines to invoice",
            cm.exception.args[0],
        )

    def test_03_force_invoiceable_lines(self):
        self.sale_order = self.env["sale.order"].browse(self.sale_order.id)
        self.sale_order.action_confirm()
        # Only the product with *Ordered quantities* policy has its line
        # quantities `to invoice`
        self.assertAlmostEqual(
            5, sum(self.sale_order.mapped("order_line.qty_to_invoice"))
        )
        self.sale_order.force_lines_to_invoice_policy_order()
        # Now the whole order qty is `to invoice`
        self.assertAlmostEqual(
            10, sum(self.sale_order.mapped("order_line.qty_to_invoice"))
        )
        # Although no quantities are delivered yet
        self.assertTrue(not any(self.sale_order.mapped("order_line.qty_delivered")))
        # Let's make the invoice
        adv_wiz = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_ids=[self.sale_order.id])
            .create({"advance_payment_method": "delivered"})
        )
        adv_wiz.with_context(open_invoices=True).create_invoices()
        self.assertEqual(10, sum(self.sale_order.mapped("order_line.qty_invoiced")))
        # We can't use the force action anymore once there's an invoice linked
        with self.assertRaises(UserError) as cm:
            self.sale_order.force_lines_to_invoice_policy_order()
        self.assertEqual(
            "You can't perform this action once the order has been invoiced "
            "once already",
            cm.exception.args[0],
        )

    @users("test-sale-manager")
    def test_03_force_invoiceable_lines_extra(self):
        self.test_03_force_invoiceable_lines()
