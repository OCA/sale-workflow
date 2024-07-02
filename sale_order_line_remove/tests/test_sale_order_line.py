# Copyright 2023 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestSaleOrderLine(TransactionCase):
    def setUp(self):
        super(TestSaleOrderLine, self).setUp()
        self.SaleOrder = self.env["sale.order"]
        self.SaleOrderLine = self.env["sale.order.line"]
        self.partner = self.env.ref("base.res_partner_2")
        self.product = self.env.ref("product.product_product_4")
        self.uom = self.env.ref("uom.product_uom_unit")

    def test_check_line_unlink(self):
        sale_order = self.SaleOrder.create({"partner_id": self.partner.id})
        sale_order.action_confirm()
        sale_order_line = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.uom.id,
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
                "product_uom": self.uom.id,
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
                "product_uom": self.uom.id,
            }
        )
        picking = sale_order.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
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
                "product_uom": self.uom.id,
            }
        )
        picking = sale_order.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
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
                "product_uom": self.uom.id,
            }
        )
        picking = sale_order.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
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
                "product_uom": self.uom.id,
            }
        )
        picking = sale_order.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
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
                "product_uom": self.uom.id,
            }
        )
        sale_order_line2 = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.uom.id,
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
