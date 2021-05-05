# Copyright 2018-2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleProcurementAmendment(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.sale_obj = cls.env["sale.order"]
        cls.sale_order_line_obj = cls.env["sale.order.line"]
        cls.product1 = cls.env.ref("product.product_product_12")
        cls.product2 = cls.env.ref("product.product_product_13")
        cls.agrolait = cls.env.ref("base.res_partner_2")

        # Create a MTO Rule on Stock - Avoid depending on purchase
        # Create another Stock location
        vals = {
            "name": "Stock MTO",
            "location_id": cls.env.ref("stock.stock_location_locations").id,
            "usage": "internal",
        }
        loc_mto = cls.env["stock.location"].create(vals)

        vals = {
            "name": "New MTO",
        }
        cls.route_mto = cls.env["stock.location.route"].create(vals)

        vals = {
            "name": "STOCK MTO -> Stock",
            "action": "pull",
            "picking_type_id": cls.env.ref("stock.picking_type_internal").id,
            "location_src_id": loc_mto.id,
            "location_id": cls.env.ref("stock.stock_location_stock").id,
            "route_id": cls.route_mto.id,
        }
        cls.env["stock.rule"].create(vals)
        cls.product1.route_ids |= cls.route_mto

    def _create_sale_order(self):

        vals = {
            "partner_id": self.agrolait.id,
        }
        self.order = self.sale_obj.create(vals)
        self.order.onchange_partner_id()
        vals = {
            "order_id": self.order.id,
            "product_id": self.product1.id,
            "product_uom_qty": 10.0,
        }
        self.sale_line = self.sale_order_line_obj.create(vals)
        self.sale_line.product_id_change()
        vals = {
            "order_id": self.order.id,
            "product_id": self.product2.id,
            "product_uom_qty": 20.0,
        }
        self.sale_line_2 = self.sale_order_line_obj.create(vals)
        self.sale_line_2.product_id_change()

    def test_00_pickings_in_progress(self):
        """
        Test the picking_in_progress and can_be_amended values
        :return:
        """
        self._create_sale_order()
        self.order.action_confirm()
        self.assertEqual(
            1,
            len(self.order.picking_ids),
        )
        self.assertTrue(
            all(
                value
                for value in self.order.picking_ids.move_lines.mapped("can_be_amended")
            )
        )
        self.assertFalse(
            self.sale_line.pickings_in_progress,
        )
        self.assertFalse(
            self.sale_line_2.pickings_in_progress,
        )

    def test_01_pickings_in_progress_op(self):
        """
        Test the picking_in_progress and can_be_amended values
        Pack operations are in progress
        :return:
        """
        self._create_sale_order()
        self.order.action_confirm()
        self.order.picking_ids.action_assign()

        self.order.picking_ids.move_line_ids.qty_done = 1.0
        self.order.picking_ids.move_lines.invalidate_cache()
        self.assertTrue(
            all(
                [
                    not value
                    for value in self.order.picking_ids.move_lines.mapped(
                        "can_be_amended"
                    )
                ]
            )
        )
        self.assertTrue(
            self.sale_line.pickings_in_progress,
        )
        self.assertTrue(
            self.sale_line_2.pickings_in_progress,
        )

    def test_02_pickings_in_progress_backorder(self):
        """
        Test the picking_in_progress and can_be_amended values
        A picking was done and a backorder is created
        :return:
        """
        self._create_sale_order()
        self.order.action_confirm()
        self.order.picking_ids.action_assign()
        self.order.picking_ids.move_line_ids.filtered(
            lambda m: m.product_id == self.product1
        ).qty_done = 1.0
        wizard = (
            self.env["stock.backorder.confirmation"]
            .with_context(button_validate_picking_ids=self.order.picking_ids.ids)
            .create({"pick_ids": [(6, 0, self.order.picking_ids.ids)]})
        )
        wizard.process()

        # The first sale line cannot be amended
        self.assertFalse(self.sale_line.can_amend_and_reprocure)
        # The second line can be amended
        self.assertTrue(self.sale_line_2.can_amend_and_reprocure)

        self.assertItemsEqual(
            [True, True, False],
            self.order.picking_ids.mapped("move_lines.can_be_amended"),
        )
        self.assertTrue(
            self.sale_line.pickings_in_progress,
        )

    def test_03_decrease_sale_line(self):
        """
        Decrease Sale Order Line
        :return:
        """
        self._create_sale_order()
        self.order.action_confirm()
        move_out = self.order.picking_ids.move_lines.filtered(
            lambda m: m.picking_id.location_dest_id.usage == "customer"
            and m.product_id == self.product1
        )
        self.assertEqual(10.0, move_out.product_uom_qty)
        # Decrease qty
        self.sale_line.write({"product_uom_qty": 9.0})
        self.assertEqual(
            "cancel",
            move_out.state,
        )

        move_out = self.order.picking_ids.mapped("move_lines").filtered(
            lambda m: m.state != "cancel"
            and m.picking_id.location_dest_id.usage == "customer"
            and m.product_id == self.product1
        )
        self.assertEqual(
            9.0,
            move_out.product_uom_qty,
        )

    def test_04_mto_rule(self):
        """
        Decrease Sale Order Line
        :return:
        """
        self.product1.route_ids += self.env.ref("stock.route_warehouse0_mto")
        self._create_sale_order()
        self.order.action_confirm()

        move_mto = self.order.picking_ids.move_lines.filtered(
            lambda line: line.location_id == self.env.ref("stock.stock_location_stock")
            and line.product_id == self.product1
        )

        self.assertEqual(
            1,
            len(move_mto),
        )
        self.assertEqual(
            10.0,
            move_mto.product_qty,
        )

        # Decrease qty
        self.sale_line.write({"product_uom_qty": 9.0})

        self.assertEqual(
            "cancel",
            move_mto.state,
        )
        move_mto = self.order.picking_ids.move_lines.filtered(
            lambda line: line.location_id == self.env.ref("stock.stock_location_stock")
            and line.product_id == self.product1
            and line.state != "cancel"
        )

        self.assertEqual(
            1,
            len(move_mto),
        )
        self.assertEqual(
            9.0,
            move_mto.product_qty,
        )

        # Decrease qty
        self.sale_line.write({"product_uom_qty": 8.0})

        self.assertEqual(
            "cancel",
            move_mto.state,
        )
        move_mto = self.order.picking_ids.move_lines.filtered(
            lambda line: line.location_id == self.env.ref("stock.stock_location_stock")
            and line.product_id == self.product1
            and line.state != "cancel"
        )
        self.assertEqual(
            1,
            len(move_mto),
        )
        # Check procurement qty
        self.assertEqual(
            8.0,
            move_mto.product_qty,
        )
        # Check move out qty
        move_out = self.order.picking_ids.mapped("move_lines").filtered(
            lambda m: m.state != "cancel"
            and m.picking_id.location_dest_id.usage == "customer"
            and m.product_id == self.product1
        )

        self.assertEqual(
            8.0,
            move_out.product_uom_qty,
        )

        # Increase qty
        self.sale_line.write({"product_uom_qty": 11.0})
        move_mto = self.order.picking_ids.move_lines.filtered(
            lambda line: line.location_id == self.env.ref("stock.stock_location_stock")
            and line.product_id == self.product1
            and line.state != "cancel"
        )
        # Check move qty - new has been added to existing one
        self.assertEqual(1, len(move_mto))
        self.assertEqual(11, sum(move_mto.mapped("product_qty")))
        # Check move out qty
        moves_out = self.order.picking_ids.mapped("move_lines").filtered(
            lambda m: m.state != "cancel"
            and m.picking_id.location_dest_id.usage == "customer"
            and m.product_id == self.product1
        )
        qty = 0.0
        for move in moves_out:
            qty += move.product_uom_qty
        self.assertEqual(
            11.0,
            qty,
        )

    def test_05_decrease_multi_sale_line(self):
        """
        Test decreasing both lines at the same time
        Check if both move out are cancelled
        Check if new moves with new quantities are created
        :return:
        """
        self._create_sale_order()
        self.order.action_confirm()
        move_out = self.order.picking_ids.move_lines.filtered(
            lambda m: m.picking_id.location_dest_id.usage == "customer"
        )
        move_product_1 = move_out.filtered(lambda m: m.product_id == self.product1)
        move_product_2 = move_out.filtered(lambda m: m.product_id == self.product2)
        self.assertEqual(10.0, move_product_1.product_uom_qty)
        self.assertEqual(20.0, move_product_2.product_uom_qty)

        # Decrease qty for both lines at the same time
        self.order.order_line.write({"product_uom_qty": 9.0})

        self.assertEqual(
            "cancel",
            move_product_1.state,
        )
        self.assertEqual(
            "cancel",
            move_product_2.state,
        )

        move_out = self.order.picking_ids.mapped("move_lines").filtered(
            lambda m: m.state != "cancel"
            and m.picking_id.location_dest_id.usage == "customer"
        )
        move_product_1 = move_out.filtered(lambda m: m.product_id == self.product1)
        move_product_2 = move_out.filtered(lambda m: m.product_id == self.product2)
        self.assertEqual(
            9.0,
            move_product_1.product_uom_qty,
        )
        self.assertEqual(
            9.0,
            move_product_2.product_uom_qty,
        )

    def test_06_pickings_done(self):
        """
        Test the picking_in_progress and can_be_amended values
        :return:
        """
        self._create_sale_order()
        self.order.action_confirm()
        self.assertEqual(
            1,
            len(self.order.picking_ids),
        )
        self.assertTrue(
            all(
                value
                for value in self.order.picking_ids.move_lines.mapped("can_be_amended")
            )
        )
        self.assertFalse(
            self.sale_line.pickings_in_progress,
        )
        self.assertFalse(
            self.sale_line_2.pickings_in_progress,
        )

        self.order.picking_ids.with_context(cancel_backorder=True)._action_done()
        self.assertFalse(
            all(
                value
                for value in self.order.picking_ids.move_lines.mapped("can_be_amended")
            )
        )
        self.assertFalse(
            self.sale_line.pickings_in_progress,
        )
        self.assertFalse(
            self.sale_line_2.pickings_in_progress,
        )

    def test_07_two_steps(self):
        """
        Change operating warehouse to manage delivery steps with Pick/Ship
        Create a sale order and confirm it
        Change quantity to 9.0
        Check original moves are cancelled and a new flow is created for
        the new quantity
        Repeat the operation decreasing quantity to 8.0
        """
        self.warehouse.delivery_steps = "pick_ship"
        self._create_sale_order()
        self.order.action_confirm()

        original_moves = self.sale_line.move_ids | self.sale_line.move_ids.mapped(
            "move_orig_ids"
        )

        self.sale_line.write({"product_uom_qty": 9.0})

        self.assertEqual(["cancel"], list(set(original_moves.mapped("state"))))
        new_moves = self.sale_line.move_ids.filtered(lambda m: m.state != "cancel")
        quantities = (new_moves | new_moves.mapped("move_orig_ids")).mapped(
            "product_uom_qty"
        )
        self.assertEqual([9.0], list(set(quantities)))

        self.sale_line.write({"product_uom_qty": 8.0})

        new_moves = self.sale_line.move_ids.filtered(lambda m: m.state != "cancel")
        quantities = (new_moves | new_moves.mapped("move_orig_ids")).mapped(
            "product_uom_qty"
        )
        self.assertEqual([8.0], list(set(quantities)))

    def test_08_three_steps(self):
        """
        Change operating warehouse to manage delivery steps with Pick/Pack/Ship
        Create a sale order and confirm it
        Transfer a product quantity of 1 on first product on picking side
        The first sale line cannot be amended
        The second line can
        """
        self.warehouse.delivery_steps = "pick_pack_ship"
        self._create_sale_order()
        self.order.action_confirm()
        picking = self.order.picking_ids.filtered(
            lambda p: p.location_id == self.env.ref("stock.stock_location_stock")
        )
        move_line = picking.move_line_ids.filtered(
            lambda m: m.product_id == self.product1
        )
        move_line.qty_done = 1.0
        wizard = (
            self.env["stock.backorder.confirmation"]
            .with_context(button_validate_picking_ids=picking.ids)
            .create({"pick_ids": [(6, 0, picking.ids)]})
        )
        wizard.process()

        self.assertTrue(self.sale_line.pickings_in_progress)
        self.assertFalse(self.sale_line_2.pickings_in_progress)
        self.assertFalse(self.sale_line.can_amend_and_reprocure)
        self.assertTrue(self.sale_line_2.can_amend_and_reprocure)
