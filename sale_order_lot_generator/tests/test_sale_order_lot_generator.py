# -*- coding: utf-8 -*-
# © 2017 Akretion, Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as test_common


class TestSaleOrderLotGenerator(test_common.SingleTransactionCase):
    def setUp(self):
        super(TestSaleOrderLotGenerator, self).setUp()
        self.product_5b = self.env.ref("product.product_product_5b")
        self.product_6 = self.env.ref("product.product_product_6")
        self.product_5b.write(
            {"tracking": "lot", "type": "product", "auto_generate_prodlot": True}
        )
        self.product_6.write(
            {"tracking": "lot", "type": "product", "auto_generate_prodlot": True}
        )

    def test_sale_order_lot_generator(self):
        # create order
        self.order1 = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_1").id,}
        )
        self.sol1 = self.env["sale.order.line"].create(
            {
                "name": "sol1",
                "order_id": self.order1.id,
                "product_id": self.product_5b.id,
                "product_uom_qty": 1,
            }
        )
        # confirm orders
        self.order1.action_confirm()
        lot_number = "%s-%03d" % (self.order1.name, 1)
        self.assertEqual(self.sol1.lot_id.name, lot_number)
        # add second line after order confirm
        self.sol2 = self.env["sale.order.line"].create(
            {
                "name": "sol1",
                "order_id": self.order1.id,
                "product_id": self.product_6.id,
                "product_uom_qty": 1,
            }
        )
        lot_number = "%s-%03d" % (self.order1.name, 2)
        self.assertEqual(self.sol2.lot_id.name, lot_number)
        picking = self.order1.picking_ids
        for move in picking.move_lines:
            if move.product_id.id == self.product_5b.id:
                self.assertEqual(move.restrict_lot_id, self.sol1.lot_id)
            if move.product_id.id == self.product_6.id:
                self.assertEqual(move.restrict_lot_id, self.sol2.lot_id)
