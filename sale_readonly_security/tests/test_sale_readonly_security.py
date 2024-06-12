# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo.exceptions import AccessError
from odoo.tests import Form, common, new_test_user
from odoo.tests.common import users
from odoo.tools import mute_logger


class TestSaleReadonlySecurity(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
                test_sale_readonly_security=True,
            )
        )
        cls.user_admin = new_test_user(
            cls.env,
            login="test_user_admin",
            groups="sales_team.group_sale_manager,%s"  # noqa:UP031
            % ("sale_readonly_security.group_sale_readonly_security_admin",),
        )
        cls.user_readonly = new_test_user(
            cls.env, login="test_user_readonly", groups="sales_team.group_sale_manager"
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "consu", "invoice_policy": "order"}
        )
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
        cls.order = order_form.save()

    @users("test_user_admin")
    @mute_logger("odoo.models.unlink")
    def test_sale_order_admin(self):
        """Read, write, unlink and create allowed."""
        orders = self.env["sale.order"].search([])
        self.assertIn(self.order, orders)
        self.order.with_user(self.env.user).write({"origin": "test"})
        self.order.with_user(self.env.user).unlink()
        new_order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.assertTrue(new_order.exists())

    @users("test_user_readonly")
    def test_sale_order_readonly(self):
        """Read allowed. Write, unlink and create not allowed."""
        orders = self.env["sale.order"].search([])
        self.assertIn(self.order, orders)
        with self.assertRaises(AccessError):
            self.order.with_user(self.env.user).write({"origin": "test"})
        with self.assertRaises(AccessError):
            self.order.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.env["sale.order"].create({"partner_id": self.partner.id})

    def test_sale_order_create_invoice(self):
        self.order.action_confirm()
        self.order.order_line.qty_delivered = 1
        with self.assertRaises(AccessError):
            self.order.with_user(self.user_readonly)._create_invoices()
        self.order.with_user(self.user_admin)._create_invoices()
