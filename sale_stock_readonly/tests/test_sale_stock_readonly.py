# Copyright 2026  Akretion (https://www.akretion.com).
# @author Sébastien Alix <sebastien.alix@akretion.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleStockReadonly(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_user = cls.env.ref("base.group_user")
        cls.group_sales_readonly = cls.env.ref(
            "sales_team_readonly.group_sales_readonly"
        )
        cls.group_stock_readonly = cls.env.ref("stock_readonly.group_stock_readonly")

        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Storable Product",
                "is_storable": True,
                "list_price": 100.0,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": cls.product.id, "product_uom_qty": 1.0}
                    ),
                ],
            }
        )
        cls.order.action_confirm()
        cls.picking = cls.order.picking_ids

        cls.user_sale_readonly = cls.env["res.users"].create(
            {
                "name": "Sales Readonly",
                "login": "sale_stock_readonly_sale",
                "group_ids": [
                    Command.link(cls.group_user.id),
                    Command.link(cls.group_sales_readonly.id),
                ],
            }
        )
        cls.user_sale_stock_readonly = cls.env["res.users"].create(
            {
                "name": "Sales Stock Readonly",
                "login": "sale_stock_readonly_user",
                "group_ids": [
                    Command.link(cls.group_user.id),
                    Command.link(cls.group_sales_readonly.id),
                    Command.link(cls.group_stock_readonly.id),
                ],
            }
        )

    def _form_arch(self, user):
        arch = self.env["sale.order"].with_user(user).get_view(view_type="form")["arch"]
        # In some environments, `get_view` returns the arch as bytes instead of str?
        if isinstance(arch, bytes):
            arch = arch.decode()
        return arch

    def test_delivery_button_visibility(self):
        self.assertIn(
            "action_view_delivery", self._form_arch(self.user_sale_stock_readonly)
        )
        self.assertNotIn(
            "action_view_delivery", self._form_arch(self.user_sale_readonly)
        )

    def test_delivery_button_opening(self):
        action = self.order.with_user(
            self.user_sale_stock_readonly
        ).action_view_delivery()
        self.assertEqual(action["res_model"], "stock.picking")
        self.assertEqual(action["res_id"], self.picking.id)
