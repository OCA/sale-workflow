# Copyright 2021 Manuel Calero Solís (http://www.xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleOrderDeliveredWeight(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderDeliveredWeight, self).setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.product_1 = self.env.ref('product.product_product_4')
        self.product_2 = self.env.ref('product.product_product_5')
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        self.sale_order_line_1 = self.env['sale.order.line'].create({
            'order_id': self.sale_order.id,
            'name': self.product_1.name,
            'product_id': self.product_1.id,
            'product_uom_qty': 2,
            'product_uom': self.product_1.uom_id.id,
        })
        self.sale_order_line_2 = self.env['sale.order.line'].create({
            'order_id': self.sale_order.id,
            'name': self.product_2.name,
            'product_id': self.product_2.id,
            'product_uom_qty': 3,
            'product_uom': self.product_2.uom_id.id,
        })

    def test_sale_order_weight(self):
        self.sale_order.action_confirm()
        self.product_1.weight = 5.0  # * 2 = 10 kg
        self.product_2.weight = 4.0  # * 0 = 0 kg
        self.sale_order_line_1.qty_delivered = self.sale_order_line_1.product_uom_qty
        self.assertEqual(self.sale_order.total_delivered_weight, 10.0)
