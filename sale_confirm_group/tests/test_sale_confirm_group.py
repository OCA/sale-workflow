# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from lxml.etree import fromstring

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import users

from .common import TestSaleConfirmGroupCommon


class TestSaleConfirmGroup(TestSaleConfirmGroupCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Dummy customer for SO creation
        cls.customer = cls.env["res.partner"].create({"name": "Customer"})

    def _create_sale(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    fields.Command.create(
                        {
                            "name": "Product",
                            "product_id": self.env.ref("product.consu_delivery_01").id,
                            "product_uom_qty": 1,
                            "price_unit": 50.00,
                        }
                    )
                ],
            }
        )

    @users("test-sale-confirm-group-user")
    def test_new_sale_user_can_confirm(self):
        company = self.env.company.sudo()
        for enabled, groups, expected in (
            (False, self.group_sale_admin, True),
            (True, self.env["res.groups"], True),
            (True, self.group_sale_admin, False),
            (True, self.group_sale_user, True),
        ):
            with self.subTest(enabled=enabled, groups=groups.ids):
                company.write(
                    {
                        "use_sale_confirmation_groups": enabled,
                        "sale_confirmation_group_ids": [fields.Command.set(groups.ids)],
                    }
                )
                sale = self.env["sale.order"].new(
                    {
                        "partner_id": self.customer.id,
                        "company_id": company.id,
                    }
                )
                self.assertFalse(sale.id)
                self.assertEqual(sale.user_can_confirm, expected)
                self.assertEqual(sale.sudo().user_can_confirm, expected)
                self.assertEqual(sale.user_can_confirm, expected)
                result = self.env["sale.order"].onchange(
                    {"company_id": company.id, "partner_id": self.customer.id},
                    [],
                    {
                        "company_id": {},
                        "partner_id": {},
                        "user_can_confirm": {},
                    },
                )
                self.assertEqual(result["value"]["user_can_confirm"], expected)

    @users("test-sale-confirm-group-user")
    def test_00_groups_usage_not_active(self):
        # Deactivate the usage of confirmation groups: the current user can confirm
        sale = self._create_sale()
        self.env.company.sudo().write(
            {
                "use_sale_confirmation_groups": False,
                "sale_confirmation_group_ids": [fields.Command.clear()],
            }
        )
        self.assertTrue(sale.user_can_confirm)
        sale.action_confirm()
        self.assertEqual(sale.state, "sale")

    @users("test-sale-confirm-group-user")
    def test_01_groups_usage_active_no_groups(self):
        # Activate the usage of confirmation groups, but remove all groups: the current
        # user can confirm
        sale = self._create_sale()
        self.env.company.sudo().write(
            {
                "use_sale_confirmation_groups": True,
                "sale_confirmation_group_ids": [fields.Command.clear()],
            }
        )
        self.assertTrue(sale.user_can_confirm)
        sale.action_confirm()
        self.assertEqual(sale.state, "sale")

    @users("test-sale-confirm-group-user")
    def test_02_groups_usage_active_with_groups(self):
        # Keep the usage of confirmation groups, keep the sale admins as the only
        # allowed group: the current user cannot confirm
        sale = self._create_sale()
        self.assertFalse(sale.user_can_confirm)
        with self.assertRaises(ValidationError) as error:
            sale.action_confirm()
        self.assertEqual(
            error.exception.args[0],
            f"User {self.env.user.name} cannot confirm"
            f" Sale(s) '{sale.display_name}'",
        )
        # Add the sale users as allowed group: the current user can now confirm
        self.env.company.sudo().sale_confirmation_group_ids += self.group_sale_user
        self.assertTrue(sale.user_can_confirm)
        sale.action_confirm()
        self.assertEqual(sale.state, "sale")
        # Remove the sale users as allowed group: the current user cannot confirm
        sale = self._create_sale()
        self.env.company.sudo().sale_confirmation_group_ids -= self.group_sale_user
        self.assertFalse(sale.user_can_confirm)
        with self.assertRaises(ValidationError) as error:
            sale.action_confirm()
        self.assertEqual(
            error.exception.args[0],
            f"User {self.env.user.name} cannot confirm"
            f" Sale(s) '{sale.display_name}'",
        )
        # Add the current user to the "Sales / Administrator" group: the current user
        # can now confirm
        self.test_user.groups_id += self.group_sale_admin
        self.assertTrue(sale.user_can_confirm)
        sale.action_confirm()
        self.assertEqual(sale.state, "sale")
        # Remove the current user from the "Sales / Administrator" group: the current
        # user cannot confirm
        sale = self._create_sale()
        self.test_user.groups_id -= self.group_sale_admin
        self.assertFalse(sale.user_can_confirm)
        with self.assertRaises(ValidationError) as error:
            sale.action_confirm()
        self.assertEqual(
            error.exception.args[0],
            f"User {self.env.user.name} cannot confirm"
            f" Sale(s) '{sale.display_name}'",
        )

    @users("test-sale-confirm-group-user")
    def test_03_context_key(self):
        # Keep the usage of confirmation groups, keep the sale admins as the only
        # allowed group: the current user cannot confirm
        sale = self._create_sale()
        self.assertFalse(sale.user_can_confirm)
        with self.assertRaises(ValidationError) as error:
            sale.action_confirm()
        self.assertEqual(
            error.exception.args[0],
            f"User {self.env.user.name} cannot confirm"
            f" Sale(s) '{sale.display_name}'",
        )
        # Add the "skip_check_user_can_confirm" context key to skip user permission
        # checks: the curren user can confirm
        sale.with_context(skip_check_user_can_confirm=True).action_confirm()
        self.assertEqual(sale.state, "sale")

    @users("test-sale-confirm-group-user")
    def test_action_confirm_invisible(self):
        view = self.env["sale.order"].get_view(view_type="form")
        arch = fromstring(view["arch"])
        self.assertTrue(arch.xpath("./field[@name='user_can_confirm'][@invisible='1']"))
        self.assertIn("user_can_confirm", view["models"]["sale.order"])
        buttons = arch.xpath("//button[@name='action_confirm']")
        self.assertTrue(buttons)
        for node in buttons:
            self.assertIn("not user_can_confirm", node.get("invisible"))
