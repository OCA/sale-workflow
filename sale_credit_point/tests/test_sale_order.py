# Copyright 2018-2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests.common import tagged

from odoo.addons.sale.tests.common import TestSaleCommon


@tagged("post_install", "-at_install")
class TestSaleOrder(TestSaleCommon):
    def setUp(self):
        super().setUp()
        self.product = self.product_a
        self.product.list_price = 10
        self.product.currency_id = self.env[
            "res.partner"
        ]._default_credit_point_currency_id()
        self.portal_user = self.env.ref("base.demo_user0").sudo()
        self.portal_user.partner_id.credit_point = 0

    def _create_so(self):
        self.product = self.product_a
        self.product.taxes_id = False
        vals = {
            "partner_id": self.partner_a.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product.name,
                        "product_id": self.product.id,
                        "product_uom_qty": 1,
                        "product_uom": self.product.uom_id.id,
                        "price_unit": self.product.list_price,
                    },
                )
            ],
        }
        so = self.env["sale.order"].create(vals)
        return so.with_context(test_sale_credit_point=True)

    def test_so_confirm_ok(self):
        so = self._create_so()
        so.partner_id.credit_point = 100
        self.assertEqual(so.state, "draft")
        so.action_confirm()
        self.assertNotEqual(so.state, "draft")
        self.assertEqual(so.partner_id.credit_point, 90)

    def test_so_confirm_not_enough_credit(self):
        so = self._create_so()
        so.partner_id.credit_point = 0
        self.assertEqual(so.state, "draft")
        with self.assertRaises(exceptions.UserError):
            so.action_confirm()

    def test_so_confirm_not_enough_credit_bypass_flag(self):
        so = self._create_so()
        so.partner_id.credit_point = 0
        self.assertEqual(so.state, "draft")
        so.with_context(skip_credit_check=True).action_confirm()
        self.assertNotEqual(so.state, "draft")
        self.assertEqual(so.partner_id.credit_point, -10)

    def test_so_confirm_not_enough_credit_bypass_group(self):
        so = self._create_so()
        so.partner_id.credit_point = 0
        self.assertEqual(so.state, "draft")
        self.env.user.groups_id |= self.env.ref(
            "sale_credit_point.group_manage_credit_point"
        )
        so.action_confirm()
        self.assertNotEqual(so.state, "draft")
        self.assertEqual(so.partner_id.credit_point, -10)

    def test_so_cancel_ok(self):
        so = self._create_so()
        so.partner_id.credit_point = 100
        so.action_confirm()
        self.assertEqual(so.state, "sale")
        self.assertEqual(so.partner_id.credit_point, 90)
        so.action_cancel()
        self.assertEqual(so.state, "cancel")
        self.assertEqual(so.partner_id.credit_point, 100)
        # Test if SO is still in draft
        so2 = self._create_so()
        so2.partner_id.credit_point = 100
        self.assertEqual(so2.state, "draft")
        self.assertEqual(so2.partner_id.credit_point, 100)
        so2.action_cancel()
        self.assertEqual(so2.state, "cancel")
        self.assertEqual(so2.partner_id.credit_point, 100)

    def test_so_credit_check_user(self):
        so = self._create_so()
        self.env.user.groups_id = [
            (4, self.env.ref("sale_credit_point.group_manage_credit_point").id)
        ]
        so.partner_id.credit_point = 0
        with self.assertRaises(exceptions.AccessError):
            # portal user doesn't have the rights
            # this is handled by record rules
            so.with_user(self.portal_user.id).credit_point_check()
        with self.assertRaises(exceptions.UserError):
            # nor can handle it via sudo with passing of the user
            so.sudo().credit_point_check(self.portal_user)
        # admin still can confirm it without check
        self.assertTrue(so.sudo().credit_point_check() is None)
