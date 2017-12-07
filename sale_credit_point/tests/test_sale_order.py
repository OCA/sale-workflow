# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.addons.sale.tests.test_sale_common import TestSale


class TestSaleOrder(TestSale):

    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.product = self.products['prod_order']
        self.product.list_price = 10
        self.product.currency_id = \
            self.env['res.partner']._default_credit_point_currency_id()

    def _create_so(self):
        self.product = self.products['prod_order']
        return self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.product.name,
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'product_uom': self.product.uom_id.id,
                    'price_unit': self.product.list_price})
            ],
        })

    def test_so_confirm_ok(self):
        so = self._create_so()
        so.partner_id.credit_point = 100
        self.assertEqual(so.state, 'draft')
        so.action_confirm()
        self.assertNotEqual(so.state, 'draft')
        self.assertEqual(so.partner_id.credit_point, 90)

    def test_so_confirm_not_enough_credit(self):
        so = self._create_so()
        so.partner_id.credit_point = 0
        self.assertEqual(so.state, 'draft')
        with self.assertRaises(exceptions.UserError):
            so.action_confirm()

    def test_so_confirm_not_enough_credit_bypass_flag(self):
        so = self._create_so()
        so.partner_id.credit_point = 0
        self.assertEqual(so.state, 'draft')
        so.with_context(skip_credit_check=True).action_confirm()
        self.assertNotEqual(so.state, 'draft')
        self.assertEqual(so.partner_id.credit_point, -10)

    def test_so_confirm_not_enough_credit_bypass_group(self):
        so = self._create_so()
        so.partner_id.credit_point = 0
        self.assertEqual(so.state, 'draft')
        self.env.user.groups_id |= \
            self.env.ref('sale_credit_point.group_manage_credit_point')
        so.action_confirm()
        self.assertNotEqual(so.state, 'draft')
        self.assertEqual(so.partner_id.credit_point, -10)
