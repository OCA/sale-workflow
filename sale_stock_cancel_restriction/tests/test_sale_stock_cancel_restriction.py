# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase


class TestSaleStockCancelRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product test", "type": "product"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner test"})
        cls.warehouse = cls.env.ref("stock.warehouse0")

    @classmethod
    def _create_sale_order(cls):
        so_form = Form(cls.env["sale.order"])
        so_form.partner_id = cls.partner
        with so_form.order_line.new() as soline_form:
            soline_form.product_id = cls.product
            soline_form.product_uom_qty = 2
        sale_order = so_form.save()
        sale_order.action_confirm()
        return sale_order

    def test_cancel_sale_order_restrict(self):
        """Validates the picking and do the assertRaises cancelling the
        order for checking that it's forbidden
        """
        sale_order = self._create_sale_order()
        picking = sale_order.picking_ids
        picking.move_ids.quantity_done = 2
        picking.button_validate()
        with self.assertRaises(UserError):
            sale_order.action_cancel()

    def test_cancel_sale_order_restrict_undelivered_picked(self):
        # Enable restrict_sale_cancel_after_delivery, and multi step delivery.
        # Cancel should be blocked only once picking is delivered
        self.warehouse.restrict_sale_cancel_after_delivery = True
        self.warehouse.delivery_steps = "pick_ship"
        sale_order = self._create_sale_order()
        pick_picking = sale_order.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "internal"
        )
        pick_picking.move_ids.quantity_done = 2
        pick_picking.button_validate()
        wizz = sale_order.action_cancel()
        self.assertEqual(
            wizz["res_model"],
            "sale.order.cancel",
        )

    def test_cancel_sale_order_restrict_undelivered_shipped(self):
        # Enable restrict_sale_cancel_after_delivery, and multi step delivery.
        # Cancel should be blocked only once picking is delivered
        self.warehouse.restrict_sale_cancel_after_delivery = True
        self.warehouse.delivery_steps = "pick_ship"
        sale_order = self._create_sale_order()
        # Pick 2 units
        pick_picking = sale_order.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "internal"
        )
        pick_picking.move_ids.quantity_done = 2
        pick_picking.button_validate()
        # Deliver 2 units
        ship_picking = sale_order.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )
        ship_picking.move_ids.quantity_done = 2
        ship_picking.button_validate()
        with self.assertRaises(UserError):
            sale_order.action_cancel()

    def test_cancel_sale_order_ok(self):
        """When canceling the order, the wizard is generated with the
        model 'sale.order.cancel
        """
        sale_order = self._create_sale_order()
        wizz = sale_order.action_cancel()
        self.assertEqual(
            wizz["res_model"],
            "sale.order.cancel",
        )
