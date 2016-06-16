# -*- coding: utf-8 -*-
import openerp.tests.common as common

class TestSaleProductLayout(common.TransactionCase):

    def setUp(self):
        super(TestSaleProductLayout, self).setUp()

        self.layout_model = self.env['sale_layout.category']
        self.line_model = self.env['sale.order.line']
        self.product_model = self.env['product.product']
        self.product = self.env.ref('product.product_product_5b')
        self.layout_cat = self.layout_model.create({
            'name': 'test layout cat',
            'subtotal': True,
            'separator': False,
            'pagebreak': False,
            'sequence': 100,
        })
        self.product.write({'section_id': self.layout_cat.id})

    def test_onchange_product(self):
        onchange_res = self.line_model.product_id_change([], self.product.id, partner_id=1)
        self.assertEqual(self.layout_cat.id, onchange_res['value']['sale_layout_cat_id'])
