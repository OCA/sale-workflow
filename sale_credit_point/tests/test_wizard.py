# Copyright 2018-2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = (
            cls.env["res.partner"]
            .with_context(tracking_disable=True)
            .create({"name": "John Wizard"})
        )
        cls.wiz_model = cls.env["wiz.manage.credit.point"]

    def _get_wiz(self, need_write=True, **kw):
        vals = {"partner_ids": [(6, 0, self.partner.ids)]}
        vals.update(**kw)
        if need_write:
            method = self.wiz_model.create
        else:
            method = self.wiz_model.new
        return method(vals)

    def _test_message(self, msg):
        self.assertIn(msg, self.partner.message_ids[0].body)

    def test_defaults(self):
        wiz = self._get_wiz(need_write=False)
        self.assertIn(self.partner.id, wiz.partner_ids.ids)

    def test_no_comment(self):
        wiz = self._get_wiz(
            need_write=False,
            operation="replace",
            credit_point=0,
        )
        with self.assertRaises(exceptions.UserError):
            wiz.action_update_credit()

    def test_credit_replace(self):
        msg = "I have money dude!"
        wiz = self._get_wiz(
            operation="replace",
            credit_point=100,
            comment=msg,
        )
        wiz.action_update_credit()
        self.assertEqual(self.partner.credit_point, 100)
        self._test_message(msg)

    def test_credit_increase(self):
        self.partner.credit_point = 10
        msg = "I have more money dude!"
        wiz = self._get_wiz(
            operation="increase",
            credit_point=10,
            comment=msg,
        )
        wiz.action_update_credit()
        self.assertEqual(self.partner.credit_point, 20)
        self._test_message(msg)

    def test_credit_decrease(self):
        self.partner.credit_point = 10
        msg = "I have less money dude!"
        wiz = self._get_wiz(
            operation="decrease",
            credit_point=10,
            comment=msg,
        )
        wiz.action_update_credit()
        self.assertEqual(self.partner.credit_point, 0)
        self._test_message(msg)
