# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

import openerp.tests.common as common


class TestExpectedDeliveryDate(common.TransactionCase):

    def setUp(self):
        super(TestExpectedDeliveryDate, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.partner_id = self.env.ref('base.res_partner_2')
        self.product_id = self.env.ref(
            'stock.product_icecream_product_template')
        self.order_id = self.sale_order_model.create({
            'partner_id': self.partner_id.id,
            'order_policy': 'picking',
            'date_expected': '2015-06-28',
            'order_line': [(0, 0, {'product_id': self.product_id.id,
                            'product_uom_qty': 1})]
        })

    def test_sale_expected_delivery_date(self):
        self.order_id.signal_workflow('order_confirm')
        if self.order_id.picking_ids:
            self.assertEqual(
                self.order_id.picking_ids[0].min_date[:10],
                self.order_id.date_expected
            )
