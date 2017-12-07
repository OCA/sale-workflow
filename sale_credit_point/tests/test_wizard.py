# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo import exceptions


class TestWizard(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestWizard, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'John Wizard',
        })
        cls.wiz_model = cls.env['wiz.manage.credit.point']

    def _get_wiz(self, **kw):
        vals = {
            'partner_ids': [(6, 0, self.partner.ids)]
        }
        vals.update(**kw)
        return self.wiz_model.new(vals)

    def _test_message(self, msg):
        self.assertIn(msg, self.partner.message_ids[0].body)

    def test_defaults(self):
        wiz = self._get_wiz()
        self.assertIn(self.partner, wiz.partner_ids)

    def test_no_comment(self):
        wiz = self._get_wiz(
            operation='replace',
        )
        with self.assertRaises(exceptions.UserError):
            wiz.action_update_credit()

    def test_credit_replace(self):
        msg = 'I have money dude!'
        wiz = self._get_wiz(
            operation='replace',
            credit_point=100,
            comment=msg,
        )
        wiz.action_update_credit()
        self.assertEqual(self.partner.credit_point, 100)
        self._test_message(msg)

    def test_credit_increase(self):
        self.partner.credit_point = 10
        msg = 'I have more money dude!'
        wiz = self._get_wiz(
            operation='increase',
            credit_point=10,
            comment=msg,
        )
        wiz.action_update_credit()
        self.assertEqual(self.partner.credit_point, 20)
        self._test_message(msg)

    def test_credit_decrease(self):
        self.partner.credit_point = 10
        msg = 'I have less money dude!'
        wiz = self._get_wiz(
            operation='decrease',
            credit_point=10,
            comment=msg,
        )
        wiz.action_update_credit()
        self.assertEqual(self.partner.credit_point, 0)
        self._test_message(msg)
