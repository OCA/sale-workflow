# -*- coding: utf-8 -*-
from openerp.tests import common


class test_product_bundle_layout(common.TransactionCase):
    """ Test Product bundle"""

    def setUp(self):
        super(test_product_bundle_layout, self).setUp()
        self.sale_order_bundle = self.env['sale.order.bundle']

    def test_add_bundle(self):
        so = self.env.ref('sale.sale_order_6')
        count_lines = len(so.order_line)
        product_bundle_without_section = self.env.ref(
            'sale_product_bundle.product_bundle_i5_computer')
        product_bundle_with_section = self.env.ref(
            'sale_product_bundle.product_bundle_services')
        so_bundle = self.sale_order_bundle.with_context(
            active_id=so.id).create(
                {'product_bundle_id': product_bundle_without_section.id,
                 'quantity': 2})
        so_bundle.add_bundle()
        so_bundle = self.sale_order_bundle.with_context(
            active_id=so.id).create(
                {'product_bundle_id': product_bundle_with_section.id,
                 'quantity': 2})
        so_bundle.add_bundle()
        # checking our sale order
        self.assertEquals(len(so.order_line), count_lines + 6)
        for line in so.order_line:
            for bundle_line in product_bundle_with_section.bundle_line_ids:
                if line.product_id.id == bundle_line.product_id.id:
                    self.assertEquals(
                        line.sale_layout_cat_id.id,
                        self.env.ref('sale_layout.sale_layout_cat_1').id)
            for bundle_line in product_bundle_without_section.bundle_line_ids:
                if line.product_id.id == bundle_line.product_id.id:
                    self.assertFalse(line.sale_layout_cat_id)
