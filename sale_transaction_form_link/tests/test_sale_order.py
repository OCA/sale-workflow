# Copyright 2024 Binhex - Zuzanna Elzbieta Szalaty Szalaty.
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from lxml import etree

from odoo.exceptions import AccessError
from odoo.tests.common import new_test_user, users

from odoo.addons.payment.tests.common import PaymentCommon


class TestSaleOrder(PaymentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_id = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_id.id,
            }
        )
        cls.provider = cls.env["payment.provider"].create(
            {
                "name": "Test",
                "code": "none",
            }
        )
        cls.user_account_invoice = new_test_user(
            cls.env,
            login="test_user_account_invoice",
            groups="account.group_account_invoice,sales_team.group_sale_manager",
        )
        cls.user_sale_salesman = new_test_user(
            cls.env,
            login="test_user_sale_salesman",
            groups="sales_team.group_sale_salesman",
        )

    def test_compute_payment_transaction_count(self):
        self.assertEqual(self.sale_order.payment_transaction_count, 0)
        transaction1 = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "partner_id": self.partner_id.id,
                "amount": 100,
                "currency_id": self.env.company.currency_id.id,
                "payment_method_id": self.payment_method.id,
            }
        )
        transaction2 = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "partner_id": self.partner_id.id,
                "amount": 200,
                "currency_id": self.env.company.currency_id.id,
                "payment_method_id": self.payment_method.id,
            }
        )
        self.sale_order.transaction_ids = [transaction1.id, transaction2.id]
        self.assertEqual(self.sale_order.payment_transaction_count, 2)
        transaction1.unlink()
        self.assertEqual(self.sale_order.payment_transaction_count, 1)

    def test_action_view_transaction(self):
        action = self.sale_order.action_view_transaction()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], "Payment Transactions")
        self.assertEqual(action["res_model"], "payment.transaction")
        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(action["domain"], [("id", "in", [])])

        transaction = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "partner_id": self.partner_id.id,
                "amount": 100,
                "currency_id": self.env.company.currency_id.id,
                "payment_method_id": self.payment_method.id,
            }
        )
        self.sale_order.transaction_ids = [transaction.id]
        action = self.sale_order.action_view_transaction()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], "Payment Transactions")
        self.assertEqual(action["res_model"], "payment.transaction")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["res_id"], transaction.id)

        transaction1 = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "partner_id": self.partner_id.id,
                "amount": 100,
                "currency_id": self.env.company.currency_id.id,
                "payment_method_id": self.payment_method.id,
            }
        )
        transaction2 = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "partner_id": self.partner_id.id,
                "amount": 200,
                "currency_id": self.env.company.currency_id.id,
                "payment_method_id": self.payment_method.id,
            }
        )
        self.sale_order.transaction_ids = [transaction1.id, transaction2.id]
        action = self.sale_order.action_view_transaction()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], "Payment Transactions")
        self.assertEqual(action["res_model"], "payment.transaction")
        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(
            action["domain"], [("id", "in", [transaction1.id, transaction2.id])]
        )

    @users("test_user_account_invoice", "test_user_sale_salesman")
    def test_form_view_button_rendered(self):
        """Checks whether the smart button is rendered for the current user

        If a test user can read the field ``payment_transaction_count`` without raising
        an ``AccessError``, then the button should be rendered.
        """
        # Quick setup:
        #   1- assign the test user as SO responsible (in sudo mode, to prevent any
        #      security-related error to be raised too soon)
        #   2- change the SO's env user to the test user: the current SO's env user is
        #      the superuser, as the SO was created in ``setUpClass()``; if we don't
        #      change it, ``AccessError`` will never be raised when reading field
        #      ``payment_transaction_count``, skewing the test
        self.sale_order.sudo().write({"user_id": self.env.uid})
        self.sale_order = self.sale_order.with_user(self.env.uid)
        try:
            self.sale_order.read(["payment_transaction_count"])
            expected = True
        except AccessError as e:
            self.assertIn("You do not have enough rights", str(e))
            expected = False
        view = self.sale_order.get_view(self.env.ref("sale.view_order_form").id)
        root = etree.fromstring(view["arch"])
        # NB: ``_Element.find()`` returns either the first child node that matches the
        # path, else ``None``
        result = root.find(".//button[@name='action_view_transaction']") is not None
        self.assertEqual(result, expected)
