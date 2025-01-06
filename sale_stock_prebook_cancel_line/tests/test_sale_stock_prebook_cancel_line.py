# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.sale_order_line_cancel.tests.common import TestSaleOrderLineCancelBase


class TestSaleStockPrebookCancelLine(TestSaleOrderLineCancelBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.draft_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product_1.name,
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.product_1.uom_id.id,
                            "price_unit": 1,
                        }
                    )
                ],
            }
        )

    def test_cancel_prebook_line_no_qty_cancelled(self):
        """If we cancel a prebook move line, the qty cancelled should be 0 on the
        sale order line
        """
        self.draft_order.reserve_stock()
        picking_reservations = self.draft_order._get_reservation_pickings()
        self.assertEqual(len(picking_reservations), 1)
        picking_reservations.move_ids._action_cancel()
        self.assertEqual(picking_reservations.move_ids.state, "cancel")
        self.assertEqual(self.draft_order.order_line.product_qty_canceled, 0)

    def test_cancel_prebook_picking_no_qty_cancelled(self):
        """If we cancel a prebook move line, the qty cancelled should be 0 on the
        sale order line
        """
        self.draft_order.reserve_stock()
        picking_reservations = self.draft_order._get_reservation_pickings()
        self.assertEqual(len(picking_reservations), 1)
        picking_reservations.action_cancel()
        self.assertEqual(picking_reservations.state, "cancel")
        self.assertEqual(self.draft_order.order_line.product_qty_canceled, 0)

    def test_cancel_prebook_no_qty_cancelled(self):
        """If we cancel a prebook move line, the qty cancelled should be 0 on the
        sale order line
        """
        self.draft_order.reserve_stock()
        picking_reservations = self.draft_order._get_reservation_pickings()
        self.assertEqual(len(picking_reservations), 1)
        self.draft_order.release_reservation()
        self.assertFalse(picking_reservations.exists())
        self.assertEqual(self.draft_order.order_line.product_qty_canceled, 0)
