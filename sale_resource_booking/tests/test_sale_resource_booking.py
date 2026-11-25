# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import suppress
from datetime import datetime

from odoo.tests import Form
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.resource_booking.tests.common import create_test_data


class SaleResourceBookingsCase(BaseCommon):
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

    def test_action_invite(self):
        order_f = Form(self.env["sale.order"])
        order_f.partner_id = self.partner
        with order_f.order_line.new() as line_f:
            line_f.product_id = self.product
        order = order_f.save()
        order.action_confirm()
        bookings = order.order_line.mapped("resource_booking_ids")
        # Open wizard
        wizard = self.env["sale.order.booking.confirm"].create(
            {"order_id": order.id, "resource_booking_ids": [(6, 0, bookings.ids)]}
        )
        self.assertEqual(order.resource_booking_count, 1)
        # Trigger invite with context
        wizard = wizard.with_context(trigger_booking_email=True)
        result = wizard.action_invite()
        self.assertEqual(result["type"], "ir.actions.client")

    def test_action_noop(self):
        # Open wizard
        order_f = Form(self.env["sale.order"])
        order_f.partner_id = self.partner
        with order_f.order_line.new() as line_f:
            line_f.product_id = self.product
        order = order_f.save()
        order.action_confirm()
        bookings = order.order_line.mapped("resource_booking_ids")
        self.assertEqual(order.resource_booking_count, 1)
        wizard = self.env["sale.order.booking.confirm"].create(
            {"order_id": order.id, "resource_booking_ids": [(6, 0, bookings.ids)]}
        )
        # Trigger noop with context
        wizard = wizard.with_context(trigger_booking_email=True)
        result = wizard.action_noop()
        self.assertEqual(result["type"], "ir.actions.client")

    def _run_action(self, action):
        """Return a recordset of applying the action results."""
        self.assertEqual(action["type"], "ir.actions.act_window")
        model = self.env[action["res_model"]].with_context(**action.get("context", {}))
        with suppress(KeyError):
            return model.browse(action["res_id"])
        with suppress(KeyError):
            return model.search(action["domain"])
        return model

    @mute_logger("odoo.models.unlink")
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
        order._action_cancel()
        self.assertEqual(bookings.mapped("state"), ["canceled"] * 2)
        # Delete SO lines, bookings deleted
        order.order_line.unlink()
        self.assertFalse(bookings.exists())

    def test_action_bookings_resync(self):
        # Create a minimal sale order with a line
        order_f = Form(self.env["sale.order"])
        order_f.partner_id = self.partner
        with order_f.order_line.new() as line_f:
            line_f.product_id = self.product
        order = order_f.save()
        order.action_confirm()
        # Call resync method
        action = order.action_bookings_resync()
        # Check it returns a valid window action
        self.assertIsInstance(action, dict)
        self.assertEqual(action.get("type"), "ir.actions.act_window")
        self.assertIn("context", action)
        self.assertEqual(action["context"].get("default_order_id"), order.id)

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
        order._action_cancel()
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

    def test_variants_different_booking_types(self):
        """Test 'Head massage' product with Duration variants (1h, 2h, 3h)."""
        rbt_1h = self.rbt.copy({"name": "Head Massage 1h", "duration": 1.0})
        rbt_2h = self.rbt.copy({"name": "Head Massage 2h", "duration": 2.0})
        rbt_3h = self.rbt.copy({"name": "Head Massage 3h", "duration": 3.0})

        attribute = self.env["product.attribute"].create({"name": "Duration"})
        val_1h = self.env["product.attribute.value"].create(
            {"name": "1 hour", "attribute_id": attribute.id}
        )
        val_2h = self.env["product.attribute.value"].create(
            {"name": "2 hours", "attribute_id": attribute.id}
        )
        val_3h = self.env["product.attribute.value"].create(
            {"name": "3 hours", "attribute_id": attribute.id}
        )

        template = self.env["product.template"].create(
            {
                "name": "Head massage",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, [val_1h.id, val_2h.id, val_3h.id])],
                        },
                    )
                ],
            }
        )

        self.assertEqual(len(template.product_variant_ids), 3)
        v_1h = template.product_variant_ids.filtered(
            lambda p: val_1h
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )
        v_2h = template.product_variant_ids.filtered(
            lambda p: val_2h
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )
        v_3h = template.product_variant_ids.filtered(
            lambda p: val_3h
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )

        # Configure booking type per variant
        v_1h.resource_booking_type_id = rbt_1h
        v_2h.resource_booking_type_id = rbt_2h
        v_3h.resource_booking_type_id = rbt_3h

        self.assertEqual(v_1h.resource_booking_type_id, rbt_1h)
        self.assertEqual(v_2h.resource_booking_type_id, rbt_2h)
        self.assertEqual(v_3h.resource_booking_type_id, rbt_3h)
        self.assertFalse(template.resource_booking_type_id)
        self.assertEqual(
            self.env["product.product"].search(
                [("resource_booking_type_id", "=", rbt_1h.id)]
            ),
            v_1h,
        )
        self.assertIn(
            template,
            self.env["product.template"].search(
                [("resource_booking_type_id", "=", rbt_3h.id)]
            ),
        )

        # Create sale order with lines for all 3 variants
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": v_1h.id, "product_uom_qty": 1}),
                    (0, 0, {"product_id": v_2h.id, "product_uom_qty": 1}),
                    (0, 0, {"product_id": v_3h.id, "product_uom_qty": 1}),
                ],
            }
        )
        order.action_confirm()

        self.assertEqual(order.resource_booking_count, 3)

        line_1h = order.order_line.filtered(lambda line: line.product_id == v_1h)
        line_2h = order.order_line.filtered(lambda line: line.product_id == v_2h)
        line_3h = order.order_line.filtered(lambda line: line.product_id == v_3h)

        booking_1h = line_1h.resource_booking_ids
        booking_2h = line_2h.resource_booking_ids
        booking_3h = line_3h.resource_booking_ids

        self.assertEqual(len(booking_1h), 1)
        self.assertEqual(len(booking_2h), 1)
        self.assertEqual(len(booking_3h), 1)

        self.assertEqual(booking_1h.type_id, rbt_1h)
        self.assertEqual(booking_1h.duration, 1.0)

        self.assertEqual(booking_2h.type_id, rbt_2h)
        self.assertEqual(booking_2h.duration, 2.0)

        self.assertEqual(booking_3h.type_id, rbt_3h)
        self.assertEqual(booking_3h.duration, 3.0)

    def test_product_without_variants_default_booking_type(self):
        """Products without variants use the booking type on template by default."""
        template = self.env["product.template"].create(
            {
                "name": "Single variant product",
                "resource_booking_type_id": self.rbt.id,
            }
        )
        self.assertEqual(len(template.product_variant_ids), 1)
        variant = template.product_variant_ids[0]
        self.assertEqual(variant.resource_booking_type_id, self.rbt)
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": variant.id, "product_uom_qty": 1}),
                ],
            }
        )
        order.action_confirm()
        self.assertEqual(order.resource_booking_count, 1)
        self.assertEqual(order.resource_booking_ids.type_id, self.rbt)
        rbt_new = self.rbt.copy({"name": "New Template Type", "duration": 3.0})
        template.resource_booking_type_id = rbt_new
        self.assertEqual(variant.resource_booking_type_id, rbt_new)

    def test_multi_variant_booking_type_isolation(self):
        """Configuring booking type on one variant does not affect other variants."""
        rbt_custom = self.rbt.copy({"name": "Custom Variant Type", "duration": 3.0})
        attribute = self.env["product.attribute"].create({"name": "Option"})
        val_a = self.env["product.attribute.value"].create(
            {"name": "Option A", "attribute_id": attribute.id}
        )
        val_b = self.env["product.attribute.value"].create(
            {"name": "Option B", "attribute_id": attribute.id}
        )

        template = self.env["product.template"].create(
            {
                "name": "Template with multiple variants",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, [val_a.id, val_b.id])],
                        },
                    )
                ],
            }
        )
        self.assertEqual(len(template.product_variant_ids), 2)
        v_a = template.product_variant_ids.filtered(
            lambda p: val_a
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )
        v_b = template.product_variant_ids.filtered(
            lambda p: val_b
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )
        v_a.resource_booking_type_id = rbt_custom
        self.assertEqual(v_a.resource_booking_type_id, rbt_custom)
        self.assertFalse(v_b.resource_booking_type_id)
        self.assertFalse(template.resource_booking_type_id)
