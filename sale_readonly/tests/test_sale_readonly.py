from odoo import Command
from odoo.exceptions import AccessError

from odoo.addons.base.tests.common import BaseCommon


class TestSaleReadonly(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_user = cls.env.ref("base.group_user")
        cls.group_salesman = cls.env.ref("sales_team.group_sale_salesman")
        cls.group_readonly = cls.env.ref("sales_team_readonly.group_sales_readonly")

        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "list_price": 100.0}
        )

        cls.user_owner = cls.env["res.users"].create(
            {
                "name": "Order Owner",
                "login": "sale_readonly_owner",
                "group_ids": [
                    Command.link(cls.group_user.id),
                    Command.link(cls.group_salesman.id),
                ],
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "user_id": cls.user_owner.id,
                "order_line": [
                    Command.create(
                        {"product_id": cls.product.id, "product_uom_qty": 1.0}
                    ),
                ],
            }
        )

        cls.user_employee = cls.env["res.users"].create(
            {
                "name": "Plain Employee",
                "login": "sale_readonly_employee",
                "group_ids": [Command.link(cls.group_user.id)],
            }
        )
        cls.user_readonly = cls.env["res.users"].create(
            {
                "name": "Sales Readonly",
                "login": "sale_readonly_user",
                "group_ids": [
                    Command.link(cls.group_user.id),
                    Command.link(cls.group_readonly.id),
                ],
            }
        )
        cls.user_salesman = cls.env["res.users"].create(
            {
                "name": "Salesman",
                "login": "sale_readonly_salesman",
                "group_ids": [
                    Command.link(cls.group_user.id),
                    Command.link(cls.group_salesman.id),
                ],
            }
        )
        cls.user_salesman_readonly = cls.env["res.users"].create(
            {
                "name": "Salesman Readonly",
                "login": "sale_readonly_salesman_readonly",
                "group_ids": [
                    Command.link(cls.group_user.id),
                    Command.link(cls.group_salesman.id),
                    Command.link(cls.group_readonly.id),
                ],
            }
        )

    def test_readonly_user_can_read_sale_order(self):
        order = self.order.with_user(self.user_readonly)
        self.assertTrue(order.read(["name", "amount_total"]))
        self.assertTrue(order.order_line.read(["name"]))

    def test_readonly_user_can_read_sale_report(self):
        self.assertTrue(
            self.env["sale.report"].with_user(self.user_readonly).search_count([])
        )

    def test_readonly_user_can_read_supporting_models(self):
        for model in (
            "account.move",
            "account.move.line",
            "account.journal",
        ):
            self.env[model].with_user(self.user_readonly).search([], limit=1)

    def test_employee_without_group_cannot_read_sale_order(self):
        with self.assertRaises(AccessError):
            self.order.with_user(self.user_employee).read(["name"])

    def test_readonly_user_cannot_create_sale_order(self):
        with self.assertRaises(AccessError):
            self.env["sale.order"].with_user(self.user_readonly).create(
                {"partner_id": self.partner.id}
            )

    def test_readonly_user_cannot_write_sale_order(self):
        with self.assertRaises(AccessError):
            self.order.with_user(self.user_readonly).write({"note": "touched"})

    def test_readonly_user_cannot_unlink_sale_order(self):
        with self.assertRaises(AccessError):
            self.order.with_user(self.user_readonly).unlink()

    def test_readonly_user_cannot_create_sale_order_line(self):
        with self.assertRaises(AccessError):
            self.env["sale.order.line"].with_user(self.user_readonly).create(
                {
                    "order_id": self.order.id,
                    "product_id": self.product.id,
                    "product_uom_qty": 1.0,
                }
            )

    def test_readonly_user_cannot_write_sale_order_line(self):
        with self.assertRaises(AccessError):
            self.order.order_line.with_user(self.user_readonly).write(
                {"product_uom_qty": 2.0}
            )

    def test_readonly_user_cannot_unlink_sale_order_line(self):
        with self.assertRaises(AccessError):
            self.order.order_line.with_user(self.user_readonly).unlink()

    def test_salesman_with_readonly_group_reads_all_orders(self):
        self.assertTrue(
            self.order.with_user(self.user_salesman_readonly).read(["name"])
        )

    def test_salesman_without_readonly_group_cannot_read_foreign_order(self):
        with self.assertRaises(AccessError):
            self.order.with_user(self.user_salesman).read(["name"])

    def test_menus_visible_for_readonly_user(self):
        visible = (
            self.env["ir.ui.menu"]
            .with_user(self.user_readonly)
            .search([])
            ._filter_visible_menus()
        )
        for xmlid in (
            "sale.menu_sale_quotations",
            "sale.menu_sale_order",
            "sale.res_partner_menu",
            "sale.product_menu_catalog",
        ):
            self.assertIn(self.env.ref(xmlid).id, visible.ids)

    def test_menus_not_visible_for_plain_employee(self):
        visible = (
            self.env["ir.ui.menu"]
            .with_user(self.user_employee)
            .search([])
            ._filter_visible_menus()
        )
        for xmlid in (
            "sale.menu_sale_quotations",
            "sale.menu_sale_order",
            "sale.res_partner_menu",
            "sale.product_menu_catalog",
        ):
            self.assertNotIn(self.env.ref(xmlid).id, visible.ids)

    def test_root_menu_visible_for_readonly_user(self):
        sale_management = (
            self.env["ir.module.module"]
            .sudo()
            .search(
                [("name", "=", "sale_management"), ("state", "=", "installed")],
                limit=1,
            )
        )
        if not sale_management:
            self.skipTest("sale_management is not installed")
        visible = (
            self.env["ir.ui.menu"]
            .with_user(self.user_readonly)
            .search([])
            ._filter_visible_menus()
        )
        self.assertIn(self.env.ref("sale.sale_menu_root").id, visible.ids)
