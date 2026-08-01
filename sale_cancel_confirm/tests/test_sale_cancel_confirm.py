# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import Form, TransactionCase


class TestSaleCancelConfirm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_7")

    def _create_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )

    def _get_cancel_wizard(self, order, reason):
        action = order.action_cancel()
        self.assertEqual(action["res_model"], "sale.order.cancel")
        wizard_form = Form(
            self.env["sale.order.cancel"].with_context(**action["context"])
        )
        wizard_form.cancel_reason = reason
        return wizard_form.save()

    def _cancel_with_reason(self, order, reason):
        wizard = self._get_cancel_wizard(order, reason)
        result = wizard.action_cancel()
        self.assertNotIsInstance(result, dict)

    def test_cancel_confirm_enabled_on_draft_order(self):
        self.env.company.sale_cancel_confirm = True
        order = self._create_order()

        self._cancel_with_reason(order, "Incorrect information")

        self.assertEqual(order.state, "cancel")
        self.assertTrue(order.cancel_confirm)
        self.assertEqual(order.cancel_reason, "Incorrect information")
        self.assertEqual(order.cancel_by, self.env.user)
        self.assertTrue(order.cancel_date)

        order.action_draft()
        self.assertFalse(order.cancel_confirm)
        self.assertFalse(order.cancel_reason)
        self.assertFalse(order.cancel_by)
        self.assertFalse(order.cancel_date)

    def test_cancel_confirm_enabled_on_confirmed_order(self):
        self.env.company.sale_cancel_confirm = True
        order = self._create_order()
        order.action_confirm()

        self._cancel_with_reason(order, "Customer request")

        self.assertEqual(order.state, "cancel")
        self.assertEqual(order.cancel_reason, "Customer request")

    def test_send_email_and_cancel(self):
        self.env.company.sale_cancel_confirm = True
        order = self._create_order()
        order.action_confirm()
        wizard = self._get_cancel_wizard(order, "Product unavailable")

        result = wizard.action_send_mail_and_cancel()

        self.assertNotIsInstance(result, dict)
        self.assertEqual(order.state, "cancel")
        self.assertEqual(order.cancel_reason, "Product unavailable")

    def test_cancel_confirm_disabled(self):
        self.env.company.sale_cancel_confirm = False
        order = self._create_order()

        result = order.action_cancel()

        self.assertNotIsInstance(result, dict)
        self.assertEqual(order.state, "cancel")
        self.assertFalse(order.cancel_confirm)
        self.assertFalse(order.cancel_reason)

    def test_company_setting(self):
        settings = self.env["res.config.settings"].create({"sale_cancel_confirm": True})

        self.assertTrue(settings.sale_cancel_confirm)
        self.assertTrue(self.env.company.sale_cancel_confirm)
