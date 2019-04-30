# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestSaleOrder, self).setUp()
        self.sale_order_model = self.env['sale.order']
        company = self.env['res.company']._company_default_get('sale.order')
        company.keep_name_so = False

    def test_enumeration(self):
        order1 = self.sale_order_model.create({
            'partner_id': self.env.ref('base.res_partner_1').id
        })
        quotation1_name = order1.name
        order2 = self.sale_order_model.create({
            'partner_id': self.env.ref('base.res_partner_1').id
        })
        quotation2_name = order2.name

        self.assertRegexpMatches(quotation1_name, 'SQ')
        self.assertRegexpMatches(quotation2_name, 'SQ')
        self.assertLess(int(quotation1_name[2:]), int(quotation2_name[2:]))

        order2.action_confirm()
        order1.action_confirm()

        self.assertRegexpMatches(order1.name, 'SO')
        self.assertEqual(order1.origin, quotation1_name)

        self.assertRegexpMatches(order2.name, 'SO')
        self.assertEqual(order2.origin, quotation2_name)
        self.assertLess(int(order2.name[2:]), int(order1.name[2:]))

    def test_with_origin(self):
        origin = 'origin'
        order1 = self.sale_order_model.create({
            'origin': origin,
            'partner_id': self.env.ref('base.res_partner_1').id
        })
        quotation1_name = order1.name
        order1.action_confirm()

        self.assertRegexpMatches(order1.name, 'SO')
        self.assertEqual(order1.origin, ', '.join([origin, quotation1_name]))

    def test_copy_no_origin(self):
        order1 = self.sale_order_model.create({
            'partner_id': self.env.ref('base.res_partner_1').id
        })
        order_copy = order1.copy()

        self.assertEqual(order1.name, order_copy.origin)

    def test_copy_with_origin(self):
        origin = 'origin'
        order1 = self.sale_order_model.create({
            'origin': origin,
            'partner_id': self.env.ref('base.res_partner_1').id
        })
        order_copy = order1.copy()

        self.assertEqual(', '.join([origin, order1.name]), order_copy.origin)
