# Copyright 2023 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.SaleOrderLine = cls.env["sale.order.line"]
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu"}
        )
        cls.uom = cls.env.ref("uom.product_uom_unit")
        cls.config_param = cls.env["ir.config_parameter"].sudo()
        cls.config_param.set_param("sale.order.line.remove", True)

    def test_check_line_unlink(self):
        sale_order = self.SaleOrder.create({"partner_id": self.partner.id})
        sale_order.action_confirm()
        sale_order_line = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom_id": self.uom.id,
            }
        )
        non_removable_lines = sale_order_line._check_line_unlink()
        self.assertFalse(non_removable_lines, "Line should not be non-removable")

    def test_unlink(self):
        sale_order = self.SaleOrder.create({"partner_id": self.partner.id})
        sale_order.action_confirm()
        sale_order_line = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom_id": self.uom.id,
            }
        )
        sale_order_line.unlink()
        self.assertFalse(sale_order_line.exists(), "Sale order line was not deleted")

    def test_check_line_not_unlinkable(self):
        sale_order = self.SaleOrder.create({"partner_id": self.partner.id})
        sale_order.action_confirm()
        sale_order_line = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom_id": self.uom.id,
            }
        )
        picking = sale_order.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.button_validate()
        with self.assertRaises(UserError):
            sale_order_line._check_line_unlink()

    def test_not_unlinkable_after_picking(self):
        sale_order = self.SaleOrder.create({"partner_id": self.partner.id})
        sale_order.action_confirm()
        sale_order_line = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom_id": self.uom.id,
            }
        )
        picking = sale_order.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.button_validate()
        with self.assertRaises(UserError):
            sale_order_line.unlink()

    def test_check_line_unlink_delivered(self):
        sale_order = self.SaleOrder.create({"partner_id": self.partner.id})
        sale_order.action_confirm()
        sale_order_line = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom_id": self.uom.id,
            }
        )
        picking = sale_order.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.button_validate()
        with self.assertRaises(UserError):
            sale_order_line._check_line_unlink()

    def test_check_line_unlink_invoiced(self):
        sale_order = self.SaleOrder.create({"partner_id": self.partner.id})
        sale_order.action_confirm()
        sale_order_line = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom_id": self.uom.id,
            }
        )
        picking = sale_order.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.button_validate()
        sale_order._create_invoices()
        with self.assertRaises(UserError):
            sale_order_line._check_line_unlink()

    def test_unlink_empty_picking(self):
        sale_order = self.SaleOrder.create({"partner_id": self.partner.id})
        sale_order.action_confirm()
        sale_order_line1 = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom_id": self.uom.id,
            }
        )
        sale_order_line2 = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom_id": self.uom.id,
            }
        )
        picking = sale_order.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()
        sale_order_line1.unlink()
        self.assertTrue(picking.exists(), "Picking was deleted")
        self.assertNotEqual(
            picking.state, "cancel", "Picking should not be cancelled yet"
        )
        sale_order_line2.unlink()
        self.assertFalse(picking.exists(), "Picking was not deleted")
