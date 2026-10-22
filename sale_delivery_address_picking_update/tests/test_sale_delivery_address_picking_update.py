# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestSaleDeliveryAddressPickingUpdate(BaseCommon):
    """Flow-oriented tests for sale_delivery_address_picking_update.

    Each test follows a realistic user scenario: confirm an order, interact
    with its pickings, change the delivery address, and verify the outcome.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")

        # A company customer with two distinct delivery addresses
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "is_company": True,
            }
        )
        cls.address1 = cls.env["res.partner"].create(
            {
                "name": "Test Address 1",
                "parent_id": cls.partner.id,
                "type": "delivery",
            }
        )
        cls.address2 = cls.env["res.partner"].create(
            {
                "name": "Test Address 2",
                "parent_id": cls.partner.id,
                "type": "delivery",
            }
        )

        # A storable product available in the warehouse
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 100,
            }
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _create_confirmed_order(self, shipping_address=None):
        """Create and confirm a sale order for 5 units of the test product."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_shipping_id": (shipping_address or self.address1).id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 5,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        return order

    def _validate_picking(self, picking):
        """Mark all move lines as fully done and validate the picking."""
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        picking._action_done()

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_pending_picking_address_auto_updated(self):
        """Changing delivery address on the sale order auto-updates pending pickings.

        Flow:
        1. Confirm a sale order with address1 → delivery picking is created.
        2. Verify picking inherits address1.
        3. Change partner_shipping_id to address2 on the sale order.
        4. Verify the pending picking partner_id is now address2 (auto-updated).
        """
        order = self._create_confirmed_order(self.address1)
        picking = order.picking_ids
        self.assertEqual(len(picking), 1)
        self.assertEqual(picking.partner_id, self.address1)

        # User changes delivery address; no manual picking update required
        order.partner_shipping_id = self.address2

        self.assertEqual(
            picking.partner_id,
            self.address2,
            "Pending picking partner_id should be automatically updated to the new "
            "delivery address.",
        )

    def test_done_picking_address_preserved(self):
        """Done pickings keep their original delivery address after a sale
        order change.

        Flow:
        1. Confirm a sale order with address1.
        2. Fully validate the delivery picking (state → done).
        3. Change partner_shipping_id to address2 on the sale order.
        4. Verify the done picking still has address1.
        """
        order = self._create_confirmed_order(self.address1)
        picking = order.picking_ids
        self._validate_picking(picking)
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.partner_id, self.address1)

        order.partner_shipping_id = self.address2

        self.assertEqual(
            picking.partner_id,
            self.address1,
            "Done picking partner_id should not be changed when the sale order "
            "delivery address is updated.",
        )

    def test_cancelled_picking_address_preserved(self):
        """Cancelled pickings keep their original delivery address after a
        sale order change.

        Flow:
        1. Confirm a sale order with address1.
        2. Cancel the delivery picking (state → cancel).
        3. Change partner_shipping_id to address2 on the sale order.
        4. Verify the cancelled picking still has address1.
        """
        order = self._create_confirmed_order(self.address1)
        picking = order.picking_ids
        picking.action_cancel()
        self.assertEqual(picking.state, "cancel")
        self.assertEqual(picking.partner_id, self.address1)

        order.partner_shipping_id = self.address2

        self.assertEqual(
            picking.partner_id,
            self.address1,
            "Cancelled picking partner_id should not be changed when the sale order "
            "delivery address is updated.",
        )

    def test_only_pending_picking_updated_when_mixed_states(self):
        """With both a done picking and a backorder, only the backorder is updated.

        Flow:
        1. Confirm a sale order with address1 (5 units).
        2. Partially validate the picking for 2 units; a backorder is created for 3.
        3. Change partner_shipping_id to address2 on the sale order.
        4. Done picking retains address1; backorder picking is updated to address2.
        """
        order = self._create_confirmed_order(self.address1)
        picking = order.picking_ids
        picking.action_assign()

        # Partially deliver 2 units so a backorder is created for the remaining 3
        for move in picking.move_ids:
            move.quantity = 2
            move.picked = True
        picking._action_done()

        self.assertEqual(picking.state, "done")

        backorder = order.picking_ids.filtered(
            lambda p: p.state not in ("done", "cancel")
        )
        self.assertTrue(
            backorder, "A backorder should have been created for the remaining units."
        )
        self.assertEqual(backorder.partner_id, self.address1)

        # Change the delivery address on the sale order
        order.partner_shipping_id = self.address2

        self.assertEqual(
            picking.partner_id,
            self.address1,
            "Done picking partner_id should remain unchanged.",
        )
        self.assertEqual(
            backorder.partner_id,
            self.address2,
            "Backorder (pending) picking partner_id should be updated to the new "
            "delivery address.",
        )

    def test_no_activity_created_on_address_change(self):
        """No warning activity is created on pending pickings when the delivery address
        is changed, because the module updates the address automatically.

        Flow:
        1. Confirm a sale order with address1.
        2. Change partner_shipping_id to address2.
        3. Verify no mail_activity_data_warning activity was scheduled on the picking.
        """
        order = self._create_confirmed_order(self.address1)
        picking = order.picking_ids

        order.partner_shipping_id = self.address2

        warning_activity_type = self.env.ref("mail.mail_activity_data_warning")
        warning_activities = picking.activity_ids.filtered(
            lambda a: a.activity_type_id == warning_activity_type
        )
        self.assertFalse(warning_activities, "No warning activity should be created.")

    def test_no_update_when_no_picking(self):
        """Changing delivery address before confirmation (no pickings yet)
        does not error.

        Flow:
        1. Create a draft sale order with address1.
        2. Change partner_shipping_id to address2 (no pickings exist yet).
        3. Confirm the order — the new picking should use address2.
        """
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_shipping_id": self.address1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 5,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )

        # Change address while still in draft (no pickings)
        order.partner_shipping_id = self.address2
        self.assertFalse(order.picking_ids)

        # Confirm; the generated picking should use the latest address
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(len(picking), 1)
        self.assertEqual(
            picking.partner_id,
            self.address2,
            "Picking created after confirmation should use the current "
            "delivery address (address2).",
        )
