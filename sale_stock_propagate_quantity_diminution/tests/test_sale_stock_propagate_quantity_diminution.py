# Copyright 2021 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestSaleStockPropagateQuantityDiminution(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ==== Warehouses ====
        warehouse0 = cls.env.ref("stock.warehouse0")
        warehouse0.update({"delivery_steps": "pick_pack_ship"})
        # ==== Sale Orders ====
        cls.order1 = cls.env.ref("sale.sale_order_1")
        cls.order1.action_confirm()
        # ==== Sale Order Lines====
        cls.line = cls.order1.order_line[0]
        # ==== Stock Moves ====
        cls.stock_move_out1 = cls.line.move_ids[0]
        cls.stock_move_pack1 = cls.stock_move_out1.move_orig_ids[0]
        cls.stock_move_pick1 = cls.stock_move_pack1.move_orig_ids[0]
        # ==== Stock Pickings ====
        cls.pick1 = cls.stock_move_pick1.picking_id
        cls.pack1 = cls.stock_move_pack1.picking_id
        cls.out1 = cls.stock_move_out1.picking_id

    def partial_delivery(self, picking, move, qty_done):
        move.write({"quantity_done": qty_done})
        wiz_act = picking.button_validate()
        wiz = Form(
            self.env[wiz_act["res_model"]].with_context(wiz_act["context"])
        ).save()
        wiz.process()

    def test_update_sale_order_line_qty_without_delivery(self):
        self.assertEqual(self.stock_move_pick1.product_uom_qty, 3)
        self.assertEqual(self.stock_move_pack1.product_uom_qty, 3)
        self.assertEqual(self.stock_move_out1.product_uom_qty, 3)
        # increase of quantities
        self.line.write({"product_uom_qty": 9})
        self.assertEqual(self.stock_move_pick1.product_uom_qty, 9)
        self.assertEqual(self.stock_move_pack1.product_uom_qty, 9)
        self.assertEqual(self.stock_move_out1.product_uom_qty, 9)
        # decrease of quantities
        self.line.write({"product_uom_qty": 2})
        self.assertEqual(self.stock_move_pick1.product_uom_qty, 2)
        self.assertEqual(self.stock_move_pack1.product_uom_qty, 2)
        self.assertEqual(self.stock_move_out1.product_uom_qty, 2)

    def test_update_sale_order_line_qty_with_partial_delivery_pick(self):
        # increase of quantities
        self.line.write({"product_uom_qty": 9})
        # partial delivery of the pick
        self.partial_delivery(self.pick1, self.stock_move_pick1, 5)
        stock_move_pick2 = self.stock_move_pack1.move_orig_ids.filtered(
            lambda r: r.state not in ["cancel", "done"]
        )
        self.assertEqual(stock_move_pick2.product_uom_qty, 4)
        # decrease of quantities
        self.line.write({"product_uom_qty": 5})
        self.assertEqual(self.stock_move_pick1.product_uom_qty, 5)
        self.assertEqual(stock_move_pick2.product_uom_qty, 0)

    def test_update_sale_order_line_qty_with_partial_delivery_pick_pack(self):
        # increase of quantities
        self.line.write({"product_uom_qty": 9})
        # partial delivery of the pick
        self.partial_delivery(self.pick1, self.stock_move_pick1, 5)
        # partial delivery of the pack
        self.partial_delivery(self.pack1, self.stock_move_pack1, 3)
        stock_move_pack2 = self.stock_move_out1.move_orig_ids.filtered(
            lambda r: r.state not in ["cancel", "done"]
        )
        self.assertEqual(stock_move_pack2.product_uom_qty, 6)
        # decrease of quantities
        self.line.write({"product_uom_qty": 5})
        self.assertEqual(self.stock_move_pick1.product_uom_qty, 5)
        self.assertEqual(self.stock_move_pack1.product_uom_qty, 3)
        self.assertEqual(self.stock_move_out1.product_uom_qty, 5)
        stock_move_pick2 = self.stock_move_pack1.move_orig_ids.filtered(
            lambda r: r.state not in ["cancel", "done"]
        )
        self.assertEqual(stock_move_pick2.product_uom_qty, 0)
        self.assertEqual(stock_move_pack2.product_uom_qty, 2)

    def test_update_sale_order_line_qty_with_partial_delivery_pick_pack_out(self):
        # increase of quantities
        self.line.write({"product_uom_qty": 9})
        # partial delivery of the pick
        self.partial_delivery(self.pick1, self.stock_move_pick1, 5)
        # partial delivery of the pack
        self.partial_delivery(self.pack1, self.stock_move_pack1, 3)
        # partial delivery of the out
        self.partial_delivery(self.out1, self.stock_move_out1, 1)
        stock_move_out2 = self.line.move_ids.filtered(
            lambda r: r.state not in ["cancel", "done"]
        )
        self.assertEqual(stock_move_out2.product_uom_qty, 8)
        # decrease of quantities
        self.line.write({"product_uom_qty": 5})
        self.assertEqual(self.stock_move_pick1.product_uom_qty, 5)
        self.assertEqual(self.stock_move_pack1.product_uom_qty, 3)
        self.assertEqual(self.stock_move_out1.product_uom_qty, 1)
        stock_move_pick2 = self.stock_move_pack1.move_orig_ids.filtered(
            lambda r: r.state not in ["cancel", "done"]
        )
        self.assertEqual(stock_move_pick2.product_uom_qty, 0)
        stock_move_pack2 = self.stock_move_out1.move_orig_ids.filtered(
            lambda r: r.state not in ["cancel", "done"]
        )
        self.assertEqual(stock_move_pack2.product_uom_qty, 2)
        self.assertEqual(stock_move_out2.product_uom_qty, 4)
