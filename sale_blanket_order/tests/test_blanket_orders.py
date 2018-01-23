# coding: utf-8
# Copyright 2018 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date, timedelta

from odoo.tests import common
from odoo import fields
from odoo.exceptions import Warning


class TestBlanketOrders(common.TransactionCase):

    def test_create_sale_orders(self):
        partner = self.env['res.partner'].create({
            'name': 'TEST',
            'customer': True,
        })
        payment_term = self.env.ref('account.account_payment_term_net')
        product = self.env['product.product'].create({
            'name': 'Demo',
            'categ_id': self.env.ref('product.product_category_1').id,
            'standard_price': 35.0,
            'list_price': 40.0,
            'type': 'consu',
            'uom_id': self.env.ref('product.product_uom_unit').id,
            'default_code': 'PROD_DEL02',
        })
        sale_pricelist = self.env['product.pricelist'].create({
            'name': 'Sale pricelist',
            'discount_policy': 'without_discount',
            'item_ids': [(0, 0, {
                'compute_price': 'fixed',
                'fixed_price': 56.0,
                'product_id': product.id,
                'applied_on': '0_product_variant',
            })]
        })
        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)

        blanket_order = self.env['sale.blanket.order'].create({
            'partner_id': partner.id,
            'validity_date': fields.Date.to_string(yesterday),
            'payment_term_id': payment_term.id,
            'pricelist_id': sale_pricelist.id,
            'lines_ids': [(0, 0, {
                'product_id': product.id,
                'product_uom': product.uom_id.id,
                'original_qty': 20.0,
                'price_unit': 1.0,  # will be updated by pricelist
            })],
        })
        blanket_order.onchange_partner_id()
        blanket_order.pricelist_id = sale_pricelist
        blanket_order.lines_ids[0].onchange_product()

        self.assertEqual(blanket_order.state, 'draft')
        self.assertEqual(blanket_order.lines_ids[0].price_unit, 56.0)

        # date in the past
        with self.assertRaises(Warning):
            blanket_order.action_confirm()

        blanket_order.validity_date = fields.Date.to_string(tomorrow)
        blanket_order.action_confirm()

        self.assertEqual(blanket_order.state, 'opened')

        wizard1 = self.env['sale.blanket.order.wizard'].with_context(
            active_id=blanket_order.id).create({})
        wizard1.lines_ids[0].write({'qty': 10.0})
        wizard1.create_sale_order()

        wizard2 = self.env['sale.blanket.order.wizard'].with_context(
            active_id=blanket_order.id).create({})
        wizard2.lines_ids[0].write({'qty': 10.0})
        wizard2.create_sale_order()

        self.assertEqual(blanket_order.state, 'expired')

        self.assertEqual(blanket_order.sale_count, 2)

        view_action = blanket_order.action_view_sale_orders()
        domain_ids = view_action['domain'][0][2]
        self.assertEqual(len(domain_ids), 2)
