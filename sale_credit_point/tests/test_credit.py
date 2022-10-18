# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests.common import SavepointCase


class TestCredit(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = (
            cls.env["res.partner"]
            .with_context(tracking_disable=True)
            .create({"name": "John Wizard"})
        )
        cls.currency = cls.env.ref("sale_credit_point.res_currency_pt")

    def test_default_currency(self):
        self.assertEqual(self.partner.credit_point_currency_id, self.currency)

    def test_default_credit(self):
        self.assertEqual(self.partner.credit_point, 0)

    def test_credit_replace(self):
        self.partner.credit_point = 10
        self.partner.credit_point_replace(100)
        self.assertEqual(self.partner.credit_point, 100)

    def test_credit_increase(self):
        self.partner.credit_point = 10
        self.partner.credit_point_increase(25)
        self.assertEqual(self.partner.credit_point, 35)

    def test_credit_decrease(self):
        self.partner.credit_point = 10
        self.partner.credit_point_decrease(5)
        self.assertEqual(self.partner.credit_point, 5)

    def _test_message(self, msg):
        self.assertIn(msg, self.partner.message_ids[0].body)

    def test_credit_replace_with_message(self):
        self.partner.credit_point = 10
        msg = "Wrong amount dude!"
        self.partner.credit_point_replace(100, comment=msg)
        self.assertEqual(self.partner.credit_point, 100)
        self._test_message(msg)

    def test_credit_increase_with_message(self):
        self.partner.credit_point = 10
        msg = "I have money dude!"
        self.partner.credit_point_increase(25, comment=msg)
        self.assertEqual(self.partner.credit_point, 35)
        self._test_message(msg)

    def test_credit_decrease_with_message(self):
        self.partner.credit_point = 10
        msg = "I less money dude!"
        self.partner.credit_point_decrease(5, comment=msg)
        self.assertEqual(self.partner.credit_point, 5)
        self._test_message(msg)

    def test_credit_cannot_be_negative(self):
        self.partner.credit_point = 10
        with self.assertRaises(exceptions.ValidationError):
            self.partner.credit_point_decrease(20)

    def test_credit_negative_bypass_flag(self):
        self.partner.credit_point = 10
        self.partner.with_context(skip_credit_check=True).credit_point_decrease(20)
        self.assertEqual(self.partner.credit_point, -10)

    def test_credit_negative_bypass_group(self):
        self.env.user.groups_id |= self.env.ref(
            "sale_credit_point.group_manage_credit_point"
        )
        self.partner.credit_point = 10
        self.partner.credit_point_decrease(20)
        self.assertEqual(self.partner.credit_point, -10)
