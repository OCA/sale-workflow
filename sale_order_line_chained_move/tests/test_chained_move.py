# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleChainedMove(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.sale_obj = cls.env["sale.order"]
        cls.sale_order_line_obj = cls.env["sale.order.line"]
        cls.product1 = cls.env.ref("product.product_product_12")
        cls.product2 = cls.env.ref("product.product_product_13")
        cls.agrolait = cls.env.ref("base.res_partner_2")

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

    def test_chained_move(self):
        """
        Change operating warehouse to manage delivery steps with Pick/Pack/Ship
        Create a sale order and confirm it
        The related moves should be 4 (2 (pack) + 2 (pick))
        """
        self.warehouse.delivery_steps = "pick_pack_ship"
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
        self.warehouse.delivery_steps = "pick_pack_ship"
        self.env["stock.rule"].search([("warehouse_id", "=", self.warehouse.id)]).write(
            {"preserve_separate_so_lines": True}
        )
        self._create_sale_order()

        vals = {
            "order_id": self.order.id,
            "product_id": self.product2.id,
            "product_uom_qty": 45.0,
        }
        sale_line_3 = self.sale_order_line_obj.create(vals)
        sale_line_3.product_id_change()
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
        self.warehouse.delivery_steps = "pick_pack_ship"

        self._create_sale_order()

        vals = {
            "order_id": self.order.id,
            "product_id": self.product2.id,
            "product_uom_qty": 45.0,
        }
        sale_line_3 = self.sale_order_line_obj.create(vals)
        sale_line_3.product_id_change()
        self.order.action_confirm()

        self.assertEqual(
            4,
            len(self.order.mapped("order_line.chained_move_ids")),
            "Move lines have been preserved instead of being merged.",
        )
