# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp.addons.sale.tests import test_sale_common


class TestSaleDoubleValidation(test_sale_common.TestSale):

    def test_one_step(self):
        so = self.so
        so.company_id.sudo().so_double_validation = 'one_step'
        # confirm quotation
        so.sudo(self.user).action_confirm()
        self.assertEquals(so.state, 'sale')

    def test_two_steps_under_limit(self):
        so = self.so
        so.company_id.sudo().so_double_validation = 'two_step'
        # confirm quotation
        so.sudo(self.user).action_confirm()
        self.assertEquals(so.state, 'sale')

    def test_two_steps_manager(self):
        so = self.so
        so.company_id.sudo().so_double_validation = 'two_step'
        so.company_id.sudo().so_double_validation_amount = 10
        # confirm quotation
        so.sudo(self.manager).action_confirm()
        self.assertEquals(so.state, 'sale')

    def test_two_steps_limit(self):
        so = self.so
        so.company_id.sudo().so_double_validation = 'two_step'
        so.company_id.sudo().so_double_validation_amount = so.amount_total
        # confirm quotation
        so.sudo(self.user).action_confirm()
        self.assertEquals(so.state, 'to_approve')
        so.sudo(self.manager).action_approve()
        self.assertEquals(so.state, 'sale')

    def test_two_steps_above_limit(self):
        so = self.so
        so.company_id.sudo().so_double_validation = 'two_step'
        so.company_id.sudo().so_double_validation_amount = 10
        # confirm quotation
        so.sudo(self.user).action_confirm()
        self.assertEquals(so.state, 'to_approve')
        so.sudo(self.manager).action_approve()
        self.assertEquals(so.state, 'sale')

    def setUp(self):
        super(TestSaleDoubleValidation, self).setUp()
        self.so = self.env['sale.order'].sudo(self.user).create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [
                (0, 0, {'name': p.name,
                        'product_id': p.id,
                        'product_uom_qty': 2,
                        'product_uom': p.uom_id.id,
                        'price_unit': p.list_price})
                for (_, p) in self.products.iteritems()
            ],
            'pricelist_id': self.env.ref('product.list0').id,
        })
        self.assertEqual(
            self.so.amount_total,
            sum([2 * p.list_price for (k, p) in self.products.iteritems()]),
            'Sale: total amount is wrong')

        # send quotation
        self.so.force_quotation_send()
        self.assertEquals(self.so.state, 'sent',
                          'Sale: state after sending is wrong')
