# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestSaleChainedMove(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.sale_obj = cls.env["sale.order"]
        cls.sale_order_line_obj = cls.env["sale.order.line"]
        cls.product1 = cls.env.ref("product.product_product_12")
        cls.product2 = cls.env.ref("product.product_product_13")
        cls.agrolait = cls.env.ref("base.res_partner_2")

        # Create new route for pick/pack/ship
        cls.warehouse.delivery_steps = "pick_pack_ship"
        cls.route = cls.env["stock.route"].create(
            {
                "name": "Route for Chained Sale Moves with Pack",
                "product_selectable": True,
            }
        )
        cls.stock_out_rule = cls.env["stock.rule"].create(
            {
                "name": "Stock -> Pack",
                "location_dest_id": cls.warehouse.wh_pack_stock_loc_id.id,
                "location_src_id": cls.env.ref("stock.stock_location_stock").id,
                "route_id": cls.route.id,
                "action": "pull",
                "picking_type_id": cls.env.ref("stock.picking_type_internal").id,
            }
        )
        cls.quality_rule = cls.env["stock.rule"].create(
            {
                "name": "Pack -> Out",
                "location_dest_id": cls.env.ref("stock.stock_location_output").id,
                "location_src_id": cls.warehouse.wh_pack_stock_loc_id.id,
                "route_id": cls.route.id,
                "procure_method": "make_to_order",
                "action": "pull",
                "picking_type_id": cls.env.ref("stock.picking_type_internal").id,
            }
        )
        cls.out_customer_rule = cls.env["stock.rule"].create(
            {
                "name": "Out -> Customers",
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "location_src_id": cls.env.ref("stock.stock_location_output").id,
                "route_id": cls.route.id,
                "procure_method": "make_to_order",
                "action": "pull",
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
            }
        )
        # Set the routes on the product
        cls.product1.route_ids = [(4, cls.route.id)]
        cls.product2.route_ids = [(4, cls.route.id)]
        return

    def _create_sale_order(self):
        vals = {
            "partner_id": self.agrolait.id,
        }
        self.order = self.sale_obj.create(vals)
        vals = {
            "order_id": self.order.id,
            "product_id": self.product1.id,
            "product_uom_qty": 10.0,
        }
        self.sale_line = self.sale_order_line_obj.create(vals)
        vals = {
            "order_id": self.order.id,
            "product_id": self.product2.id,
            "product_uom_qty": 20.0,
        }
        self.sale_line_2 = self.sale_order_line_obj.create(vals)

    def test_chained_move(self):
        """
        Create a sale order and confirm it
        The related moves should be 4 (2 (pack) + 2 (pick))
        """
        self._create_sale_order()
        self.order.action_confirm()

        self.assertEqual(
            4,
            len(self.order.mapped("order_line.chained_move_ids")),
        )
        moves = self.order.mapped("order_line.move_ids")
        chained_moves = self.order.mapped("order_line.chained_move_ids")
        self.assertTrue(
            all(move not in chained_moves for move in moves),
            "Some moves also appear in the chained moves",
        )

    def test_chained_move_same_product_preserve(self):
        """
        Check that multiple lines of the same product are not
        merged together if the option is activated
        """
        self.route.rule_ids.write({"preserve_separate_so_lines": True})
        self._create_sale_order()

        vals = {
            "order_id": self.order.id,
            "product_id": self.product2.id,
            "product_uom_qty": 45.0,
        }
        self.sale_order_line_obj.create(vals)
        self.order.action_confirm()

        self.assertEqual(
            6,
            len(self.order.mapped("order_line.chained_move_ids")),
            "Move lines have not been preserved",
        )

        moves = self.order.mapped("order_line.move_ids")
        chained_moves = self.order.mapped("order_line.chained_move_ids")
        self.assertTrue(
            all(move not in chained_moves for move in moves),
            "Some moves also appear in the chained moves",
        )

    def test_chained_move_same_product(self):
        """
        If preserve_separate_so_lines is not active for
        a specific type of rule, keep the default behaviour and merge them
        """
        self._create_sale_order()

        vals = {
            "order_id": self.order.id,
            "product_id": self.product2.id,
            "product_uom_qty": 45.0,
        }
        self.sale_order_line_obj.create(vals)
        self.order.action_confirm()

        self.assertEqual(
            4,
            len(self.order.mapped("order_line.chained_move_ids")),
            "Move lines have been preserved instead of being merged.",
        )
