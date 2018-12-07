# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from odoo import fields
from odoo.exceptions import ValidationError
from .common import SaleCountryRestrictionCommon


class TestSaleRestriction(SaleCountryRestrictionCommon):

    def test_sale_restriction(self):
        line = self.line_obj.new({
            'order_id': self.sale_order.id,
            'product_id': self.product_2.id,
        })
        with mock.patch.object(fields.Date, 'today') as today:
            today.return_value = '2018-03-20'
            res = line._onchange_product_country_restriction()
            self.assertIn('message', res.get('warning'))

            vals = line._convert_to_write(line._cache)
            self.line_obj.create(vals)

            with self.assertRaises(ValidationError):
                self.sale_order.action_confirm()

    def test_sale_restriction_no_match(self):
        # Add a restriction that does not match shipping id
        self.partner.country_restriction_id = self.restriction_1
        line = self.line_obj.new({
            'order_id': self.sale_order.id,
            'product_id': self.product_2.id,
        })
        with mock.patch.object(fields.Date, 'today') as today:
            today.return_value = '2018-03-20'
            res = line._onchange_product_country_restriction()
            self.assertFalse(res)

    def test_sale_restriction_partner(self):
        self.partner.country_restriction_id = False
        self.line_obj.create({
            'order_id': self.sale_order.id,
            'product_id': self.product_2.id,
        })

        vals = {
            'partner_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
        }

        self.sale_order = self.env['sale.order'].create(vals)
        with self.assertRaises(ValidationError):
            self.sale_order.action_confirm()

        self.partner.country_restriction_id = self.restriction_1
        self.sale_order.action_confirm()
        self.assertEquals(
            'sale',
            self.sale_order.state,
        )

    def test_partner(self):
        self.partner.country_id = False
        vals = {
            'partner_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
        }

        self.sale_order = self.env['sale.order'].new(vals)
        res = self.sale_order._onchange_partners_check_country()
        self.assertIn('warning', res)

        self.partner.country_id = self.kp
        res = self.sale_order._onchange_partners_check_country()
        self.assertNotIn('warning', res)

        self.partner.restriction_id = False
        self.sale_order._onchange_partners_check_restriction()
        self.assertIn('warning', res)
