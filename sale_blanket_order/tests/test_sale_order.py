# Copyright (C) 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date, timedelta

from odoo.tests import common
from odoo import fields


class TestSaleOrder(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.blanket_order_obj = self.env['sale.blanket.order']
        self.blanket_order_line_obj = self.env['sale.blanket.order.line']
        self.sale_order_obj = self.env['sale.order']
        self.sale_order_line_obj = self.env['sale.order.line']

        self.partner = self.env['res.partner'].create({
            'name': 'TEST SUPPLIER',
            'customer': True,
        })
        self.payment_term = self.env.ref('account.account_payment_term_net')
        self.sale_pricelist = self.env['product.pricelist'].create({
            'name': 'Test Pricelist',
            'currency_id': self.env.ref('base.USD').id,
        })

        self.product = self.env['product.product'].create({
            'name': 'Demo',
            'categ_id': self.env.ref('product.product_category_1').id,
            'standard_price': 40.0,
            'type': 'consu',
            'uom_id': self.env.ref('uom.product_uom_unit').id,
            'default_code': 'PROD_DEL01',
        })
        self.product_2 = self.env['product.product'].create({
            'name': 'Demo 2',
            'categ_id': self.env.ref('product.product_category_1').id,
            'standard_price': 35.0,
            'type': 'consu',
            'uom_id': self.env.ref('uom.product_uom_unit').id,
            'default_code': 'PROD_DEL02',
        })
        self.validity = date.today() + timedelta(days=365)
        self.date_schedule_1 = date.today() + timedelta(days=10)
        self.date_schedule_2 = date.today() + timedelta(days=20)

    def create_blanket_order_01(self):
        blanket_order = self.blanket_order_obj.create({
            'partner_id': self.partner.id,
            'validity_date': fields.Date.to_string(self.validity),
            'payment_term_id': self.payment_term.id,
            'pricelist_id': self.sale_pricelist.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'date_schedule': fields.Date.to_string(self.date_schedule_1),
                'original_uom_qty': 20.0,
                'price_unit': 30.0,
            }), (0, 0, {
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'date_schedule': fields.Date.to_string(self.date_schedule_2),
                'original_uom_qty': 20.0,
                'price_unit': 30.0,
            })],
        })
        blanket_order.sudo().onchange_partner_id()
        return blanket_order

    def create_blanket_order_02(self):
        blanket_order = self.blanket_order_obj.create({
            'partner_id': self.partner.id,
            'validity_date': fields.Date.to_string(self.validity),
            'payment_term_id': self.payment_term.id,
            'pricelist_id': self.sale_pricelist.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'original_uom_qty': 20.0,
                'price_unit': 30.0,
            }), (0, 0, {
                'product_id': self.product_2.id,
                'product_uom': self.product.uom_id.id,
                'original_uom_qty': 20.0,
                'price_unit': 30.0,
            })],
        })
        blanket_order.sudo().onchange_partner_id()
        return blanket_order

    def test_01_create_sale_order(self):
        blanket_order = self.create_blanket_order_01()
        blanket_order.sudo().action_confirm()
        bo_lines = self.blanket_order_line_obj.search([
            ('order_id', '=', blanket_order.id),
        ])
        self.assertEqual(len(bo_lines), 2)

        so = self.sale_order_obj.create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.product.name,
                    'product_id': self.product.id,
                    'product_uom_qty': 5.0,
                    'product_uom': self.product.uom_po_id.id,
                    'price_unit': 10.0,
                })
            ]
        })
        so_line = so.order_line[0]
        so_line.with_context(from_sale_order=True).name_get()
        so_line.onchange_product_id()
        self.assertEqual(so_line._get_eligible_bo_lines(), bo_lines)
        bo_line_assigned = self.blanket_order_line_obj.search([
            ('date_schedule', '=', fields.Date.to_string(self.date_schedule_1))
        ])
        self.assertEqual(so_line.blanket_order_line, bo_line_assigned)

    def test_02_create_sale_order(self):
        blanket_order = self.create_blanket_order_02()
        blanket_order.sudo().action_confirm()
        bo_lines = self.blanket_order_line_obj.search([
            ('order_id', '=', blanket_order.id),
        ])
        self.assertEqual(len(bo_lines), 2)

        so = self.sale_order_obj.create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.product.name,
                    'product_id': self.product.id,
                    'product_uom_qty': 5.0,
                    'product_uom': self.product.uom_po_id.id,
                    'price_unit': 10.0,
                })
            ]
        })
        so_line = so.order_line[0]
        so_line.with_context(from_sale_order=True).name_get()
        so_line.onchange_product_id()
        self.assertEqual(so_line._get_eligible_bo_lines(), bo_lines.filtered(
            lambda l: l.product_id == self.product))
        bo_line_assigned = self.blanket_order_line_obj.search([
            ('order_id', '=', blanket_order.id),
            ('product_id', '=', self.product.id),
            ('date_schedule', '=', False)
        ])
        self.assertEqual(so_line.blanket_order_line, bo_line_assigned)
