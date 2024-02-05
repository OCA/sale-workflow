# Copyright 2021 Manuel Calero Solís (http://www.xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleOrderWeight(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.product_1 = self.env.ref('product.product_product_4')
        self.product_1.weight = 5.0  # * 2 = 10 kg
        self.product_2 = self.env.ref('product.product_product_5')
        self.product_2.weight = 4.0  # * 3 = 12 kg
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        self.sale_order_line_1 = self.env['sale.order.line'].create({
            'order_id': self.sale_order.id,
            'name': self.product_1.name,
            'product_id': self.product_1.id,
            'unit_weight': self.product_1.weight,
            'product_uom_qty': 2,
            'product_uom': self.product_1.uom_id.id,
        })
        self.sale_order_line_2 = self.env['sale.order.line'].create({
            'order_id': self.sale_order.id,
            'name': self.product_2.name,
            'product_id': self.product_2.id,
            'unit_weight': self.product_2.weight,
            'product_uom_qty': 3,
            'product_uom': self.product_2.uom_id.id,
        })

    def test_sale_order_weight(self):
        self.assertEqual(self.sale_order.total_ordered_weight, 22.0)
        self.sale_order_line_1.product_uom_qty = 1
        self.assertEqual(self.sale_order.total_ordered_weight, 17.0)

    def test_sale_delivered_weight(self):
        self.sale_order.action_confirm()
        picking_1 = self.sale_order.picking_ids
        self.assertEqual(len(picking_1.move_lines), 2)
        picking_1.action_confirm()
        picking_1.mapped('move_lines').write({'quantity_done': 1})
        picking_1.action_done()
        self.assertEqual(self.sale_order.total_delivered_weight, 9.0)

    def test_sale_order_recalculate_weight(self):
        self.product_1.weight = 10.0  # * 2 = 20 kg
        self.sale_order.recalculate_weight()
        self.assertEqual(self.sale_order.total_ordered_weight, 32.0)
