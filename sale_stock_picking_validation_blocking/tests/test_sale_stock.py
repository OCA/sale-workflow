# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestSaleStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.manager = new_test_user(
            cls.env,
            login="test_sale_manager",
            groups="sales_team.group_sale_manager,stock.group_stock_user",
        )
        cls.salesman = new_test_user(
            cls.env,
            login="test_salesman",
            groups="sales_team.group_sale_salesman,stock.group_stock_user",
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu"}
        )
        cls.sale_order = (
            cls.env["sale.order"]
            .with_user(cls.manager)
            .create(
                {
                    "partner_id": cls.partner.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": cls.product.id,
                                "product_uom_qty": 10.0,
                            },
                        )
                    ],
                }
            )
        )

    def _set_full_quantity(self, picking):
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty

    def test_sale_stock_picking_validation_blocked(self):
        order = self.sale_order
        self.assertTrue(order.hide_button_picking_validation_blocked)
        order.action_confirm()
        order.invalidate_recordset(["hide_button_picking_validation_blocked"])
        self.assertFalse(order.hide_button_picking_validation_blocked)
        picking = order.picking_ids
        self.assertEqual(len(picking), 1)
        self._set_full_quantity(picking)
        self.assertFalse(order.picking_validation_blocked)
        self.assertFalse(picking.validation_blocked_by_so)

        order.action_block_picking_validation()
        self.assertTrue(order.picking_validation_blocked)
        self.assertTrue(picking.validation_blocked_by_so)
        with self.assertRaises(ValidationError):
            picking.with_user(self.manager).button_validate()
        self.assertNotEqual(picking.state, "done")

        order.action_unblock_picking_validation()
        self.assertFalse(picking.validation_blocked_by_so)
        picking.with_user(self.manager).button_validate()
        self.assertEqual(picking.state, "done")

    def test_hide_buttons_for_salesman(self):
        self.sale_order.action_confirm()
        order = self.sale_order.with_user(self.salesman)
        self.assertTrue(order.hide_button_picking_validation_blocked)

    def test_hide_buttons_without_delivery(self):
        service = self.env["product.product"].create(
            {"name": "Test Service", "type": "service"}
        )
        order = (
            self.env["sale.order"]
            .with_user(self.manager)
            .create(
                {
                    "partner_id": self.partner.id,
                    "order_line": [(0, 0, {"product_id": service.id})],
                }
            )
        )
        order.action_confirm()
        self.assertEqual(order.delivery_count, 0)
        self.assertTrue(order.hide_button_picking_validation_blocked)
