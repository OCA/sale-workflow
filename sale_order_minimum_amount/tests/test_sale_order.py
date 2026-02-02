from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, new_test_user, tagged, users

from odoo.addons.sale.tests.common import SaleCommon


@tagged("-at_install", "post_install")
class TestSaleOrder(SaleCommon, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure sale order has low total to trigger the UserError
        cls.sale_order.order_line.write({"price_unit": 10.0})
        cls.env.company.sale_min_order_limit = 500.0
        cls.test_user = new_test_user(
            cls.env,
            login="test_user",
        )

    @users("test_user")
    def test_00_usererror_on_sale_order_confirmation(self):
        """New method to raise UserError on confirming the sale order when total
        amount is less than 500 for the user who are not not sales manager."""
        with self.assertRaises(UserError):
            self.sale_order.with_user(self.env.user).action_confirm()

    def test_01_sale_order_confirm(self):
        """New method to check that sale order is confirmed if total amount is greater
        than 500."""
        self.sale_order.order_line.write({"price_unit": 600})
        self.sale_order.action_confirm()
        # Assert that check sale order is confirmed or not.
        self.assertEqual(self.sale_order.state, "sale", "Sale order is not confirmed")

    @users("test_user")
    def test_02_confirm_order_below_limit_with_user_rights(self):
        """New method should confirm order if user has Sales Manager rights
        even if amount < limit."""
        # Ensure the user has the necessary rights to bypass the minimum order limit
        self.test_user.groups_id |= self.env.ref("sales_team.group_sale_manager")
        self.sale_order.with_user(self.env.user).action_confirm()
        # Verify that the sale order is confirmed
        self.assertEqual(self.sale_order.state, "sale", "Sale order is not confirmed")
