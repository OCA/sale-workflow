# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestSaleStockPropagateQuantityDiminution(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ==== Warehouses ====
        warehouse0 = cls.env.ref("stock.warehouse0")
        warehouse0.update({"delivery_steps": "pick_pack_ship"})

        # Product
        create_product = cls.env["product.product"].create
        cls.pack_product = create_product({"name": "Pack"})
        cls.comp_product_1 = create_product({"name": "Comp 1"})
        cls.comp_product_2 = create_product({"name": "Comp 2"})
        cls.bom = cls.env["mrp.bom"].create(
            {
                "type": "phantom",
                "product_tmpl_id": cls.pack_product.product_tmpl_id.id,
                "product_id": cls.pack_product.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.comp_product_1.id, "product_qty": 3}),
                    (0, 0, {"product_id": cls.comp_product_2.id, "product_qty": 2}),
                ],
            }
        )
        # ==== Sale Orders ====
        cls.order1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.env["res.partner"].create({"name": "FOO"}).id,
                "order_line": [
                    (0, 0, {"product_id": cls.pack_product.id, "product_uom_qty": 2})
                ],
            }
        )
        cls.order1.action_confirm()
        # ==== Sale Order Lines====
        cls.line = cls.order1.order_line[0]
        # ==== Stock Moves ====
        cls.comp1_out1 = cls.line.move_ids[0]
        cls.comp1_pack1 = cls.comp1_out1.move_orig_ids[0]
        cls.comp1_pick1 = cls.comp1_pack1.move_orig_ids[0]

        cls.comp2_out1 = cls.line.move_ids[1]
        cls.comp2_pack1 = cls.comp2_out1.move_orig_ids[0]
        cls.comp2_pick1 = cls.comp2_pack1.move_orig_ids[0]

        # ==== Stock Pickings ====
        cls.pick1 = cls.comp1_pick1.picking_id
        cls.pack1 = cls.comp1_pack1.picking_id
        cls.out1 = cls.comp1_out1.picking_id

    def partial_delivery(self, picking):
        wiz_act = picking.button_validate()
        wiz = Form(
            self.env[wiz_act["res_model"]].with_context(wiz_act["context"])
        ).save()
        wiz.process()

    def test_update_sale_order_line_qty_without_delivery(self):
        self.assertEqual(self.comp1_pick1.product_uom_qty, 6)
        self.assertEqual(self.comp1_pack1.product_uom_qty, 6)
        self.assertEqual(self.comp1_out1.product_uom_qty, 6)

        self.assertEqual(self.comp2_pick1.product_uom_qty, 4)
        self.assertEqual(self.comp2_pack1.product_uom_qty, 4)
        self.assertEqual(self.comp2_out1.product_uom_qty, 4)

        # increase of quantities
        self.line.write({"product_uom_qty": 3})

        self.assertEqual(self.comp1_pick1.product_uom_qty, 9)
        self.assertEqual(self.comp1_pack1.product_uom_qty, 9)
        self.assertEqual(self.comp1_out1.product_uom_qty, 9)

        self.assertEqual(self.comp2_pick1.product_uom_qty, 6)
        self.assertEqual(self.comp2_pack1.product_uom_qty, 6)
        self.assertEqual(self.comp2_out1.product_uom_qty, 6)

        # decrease of quantities
        self.line.write({"product_uom_qty": 1})
        self.assertEqual(self.comp1_pick1.product_uom_qty, 3)
        self.assertEqual(self.comp1_pack1.product_uom_qty, 3)
        self.assertEqual(self.comp1_out1.product_uom_qty, 3)

        self.assertEqual(self.comp2_pick1.product_uom_qty, 2)
        self.assertEqual(self.comp2_pack1.product_uom_qty, 2)
        self.assertEqual(self.comp2_out1.product_uom_qty, 2)

    def test_update_sale_order_line_qty_with_partial_delivery_pick(self):
        # increase of quantities
        self.line.write({"product_uom_qty": 3})
        # partial delivery of the pick
        self.comp1_pick1.write({"quantity_done": 7})
        self.comp2_pick1.write({"quantity_done": 6})
        self.partial_delivery(self.pick1)

        comp1_pick2 = self.comp1_pack1.move_orig_ids.filtered(
            lambda r: r.state not in ["cancel", "done"]
        )

        self.assertEqual(comp1_pick2.product_uom_qty, 2)

        # Decrease of quantities
        self.line.write({"product_uom_qty": 2})
        self.assertEqual(comp1_pick2.product_uom_qty, 0)
        self.assertEqual(comp1_pick2.state, "cancel")

        self.assertEqual(self.comp1_pack1.product_uom_qty, 6)
        self.assertEqual(self.comp1_out1.product_uom_qty, 6)

        self.assertEqual(self.comp2_pack1.product_uom_qty, 4)
        self.assertEqual(self.comp2_out1.product_uom_qty, 4)
