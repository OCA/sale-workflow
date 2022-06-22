# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleChainedMove(common.SavepointCase):
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
        self.assertNotIn(
            self.order.mapped("order_line.move_ids").ids,
            self.order.mapped("order_line.chained_move_ids").ids,
        )
