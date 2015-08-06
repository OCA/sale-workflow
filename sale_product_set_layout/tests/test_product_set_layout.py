# -*- coding: utf-8 -*-
from openerp.tests import common


class test_product_set_layout(common.TransactionCase):
    """ Test Product set"""

    def setUp(self):
        super(test_product_set_layout, self).setUp()
        self.sale_order_set = self.env['sale.order.set']

    def test_add_set(self):
        so = self.env.ref('sale.sale_order_6')
        count_lines = len(so.order_line)
        product_set_without_section = self.env.ref(
            'sale_product_set.product_set_i5_computer')
        product_set_with_section = self.env.ref(
            'sale_product_set.product_set_services')
        so_set = self.sale_order_set.with_context(
            active_id=so.id).create(
                {'product_set_id': product_set_without_section.id,
                 'quantity': 2})
        so_set.add_set()
        so_set = self.sale_order_set.with_context(
            active_id=so.id).create(
                {'product_set_id': product_set_with_section.id,
                 'quantity': 2})
        so_set.add_set()
        # checking our sale order
        self.assertEquals(len(so.order_line), count_lines + 6)
        for line in so.order_line:
            for set_line in product_set_with_section.set_line_ids:
                if line.product_id.id == set_line.product_id.id:
                    self.assertEquals(
                        line.sale_layout_cat_id.id,
                        self.env.ref('sale_layout.sale_layout_cat_1').id)
            for set_line in product_set_without_section.set_line_ids:
                if line.product_id.id == set_line.product_id.id:
                    self.assertFalse(line.sale_layout_cat_id)
