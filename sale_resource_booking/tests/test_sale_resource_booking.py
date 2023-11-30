# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import suppress
from datetime import datetime

from odoo.tests.common import Form, TransactionCase

from odoo.addons.resource_booking.tests.common import create_test_data


class SaleResourceBookingsCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_data(cls)
        cls.product = cls.env["product.product"].create(
            {"name": "test booking product", "resource_booking_type_id": cls.rbt.id}
        )
        cls.product_normal = cls.env["product.product"].create(
            {"name": "test non-booking product"}
        )

    def _run_action(self, action):
        """Return a recordset of applying the action results."""
        self.assertEqual(action["type"], "ir.actions.act_window")
        model = self.env[action["res_model"]].with_context(**action.get("context", {}))
        with suppress(KeyError):
            return model.browse(action["res_id"])
        with suppress(KeyError):
            return model.search(action["domain"])
        return model

    def _test_wizard_quotation(self, combination_rel):
        """Test quotation wizard."""
        assert combination_rel._name == "resource.booking.type.combination.rel"
        partner2 = self.partner.copy()
        # No bookings to begin
        self.assertFalse(self.rbt.booking_ids)
        self.assertEqual(self.rbt.booking_count, 0)
        # Click "Quote" button
        action = self.rbt.action_sale_order_wizard()
        wiz_f = Form(self._run_action(action))
        wiz_f.partner_id = self.partner
        wiz_f.product_id = self.product
        wiz_f.product_uom_qty = 2
        # Click "Generate quotation" button on wizard
        wiz = wiz_f.save()
        action = wiz.action_generate()
        order = self._run_action(action)
        # SO is quotation, no bookings yet
        self.assertEqual(order._name, "sale.order")
        self.assertEqual(order.state, "draft")
        self.assertEqual(order.resource_booking_count, 0)
        self.assertFalse(order.resource_booking_ids)
        self.assertFalse(self.rbt.booking_ids)
        self.assertEqual(self.rbt.booking_count, 0)
        # Confirm SO, 2 bookings created
        action = order.action_confirm()
        self.assertEqual(order.resource_booking_count, 2)
        self.assertTrue(order.resource_booking_ids)
        self.assertTrue(self.rbt.booking_ids)
        self.assertEqual(self.rbt.booking_count, 2)
        # Add new attendees
        for booking in order.resource_booking_ids:
            booking.partner_ids += partner2
        # Click on "Bookings" smart button
        action = order.action_open_resource_bookings()
        bookings = self._run_action(action)
        self.assertEqual(bookings, self.rbt.booking_ids)
        self.assertEqual(bookings, order.resource_booking_ids)
        for booking in bookings:
            self.assertEqual(booking.type_id, self.rbt)
            self.assertEqual(booking.state, "pending")
            self.assertEqual(booking.combination_id, combination_rel.combination_id)
            self.assertFalse(booking.start)
            self.assertFalse(booking.stop)
            self.assertFalse(booking.meeting_id)
            self.assertEqual(order.partner_id, booking.partner_id)
            self.assertTrue(partner2 in booking.partner_ids)
        if self.product.resource_booking_type_combination_rel_id:
            self.assertEqual(bookings.mapped("combination_auto_assign"), [False] * 2)
            self.assertEqual(
                bookings.combination_id,
                self.product.resource_booking_type_combination_rel_id.combination_id,
            )
        else:
            self.assertEqual(bookings.mapped("combination_auto_assign"), [True] * 2)
        # Cancel SO, bookings canceled
        order.action_cancel()
        self.assertEqual(bookings.mapped("state"), ["canceled"] * 2)
        # Delete SO lines, bookings deleted
        order.order_line.unlink()
        self.assertFalse(bookings.exists())

    def test_wizard_quotation_product_no_rbc(self):
        """Test quotation wizard when product has no combination assigned."""
        rbcr = self.env["resource.booking.type.combination.rel"]
        self._test_wizard_quotation(rbcr)

    def test_wizard_quotation_product_with_rbc(self):
        """Test quotation wizard when product has a combination assigned."""
        rbcr = self.rbt.combination_rel_ids[0]
        self.product.resource_booking_type_combination_rel_id = rbcr
        self._test_wizard_quotation(rbcr)

    def test_order_state_limits_booking_state(self):
        """Unconfirmed orders cannot get confirmed bookings."""
        # Create quotation
        order_f = Form(self.env["sale.order"])
        order_f.partner_id = self.partner
        with order_f.order_line.new() as line_f:
            line_f.product_id = self.product
        with order_f.order_line.new() as line_f:
            line_f.product_id = self.product_normal
        order = order_f.save()
        # No bookings autocreated yet
        self.assertFalse(order.resource_booking_ids)
        # Confirm order; bookings pending
        order.action_confirm()
        booking = order.resource_booking_ids
        self.assertTrue(booking)
        self.assertEqual(booking.state, "pending")
        # Cancel order; booking canceled
        order.action_cancel()
        self.assertEqual(booking.state, "canceled")
        # Manually set order and booking to pending
        order.action_draft()
        booking.toggle_active()
        self.assertEqual(booking.state, "pending")
        # Schedule it
        with Form(booking) as booking_f:
            booking_f.start = datetime(2021, 3, 1, 10)
        self.assertEqual(booking.state, "scheduled")
        # Try to confirm it, but it still gets as scheduled
        booking.action_confirm()
        self.assertEqual(booking.state, "scheduled")
        # Confirming order, the booking is confirmed too
        order.action_confirm()
        self.assertEqual(booking.state, "confirmed")
