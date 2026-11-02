# Copyright 2026 Tohid Pathan (Allied Vision Technologies Pvt. Ltd.)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError, UserError
from odoo.fields import Command
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPortalDeliveryAddress(TransactionCase):
    """Unit tests for portal delivery address models.

    Covers:
    - AC1, AC2, AC3: Address creation and listing.
    - AC4, AC5: Shipping address update on sale orders.
    - AC7: Address archiving.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ------------------------------------------------------------------ #
        # Company A setup                                                      #
        # ------------------------------------------------------------------ #
        cls.company_a = cls.env["res.partner"].create(
            {"name": "Company A", "is_company": True}
        )
        cls.portal_user_a = cls.env["res.users"].create(
            {
                "name": "Portal User A",
                "login": "portal_user_a@test.com",
                "email": "portal_user_a@test.com",
                "group_ids": [
                    Command.link(cls.env.ref("base.group_portal").id),
                ],
                "partner_id": cls.env["res.partner"]
                .create(
                    {
                        "name": "Portal User A",
                        "parent_id": cls.company_a.id,
                        "type": "contact",
                    }
                )
                .id,
            }
        )

        # ------------------------------------------------------------------ #
        # Company B setup (separate tenant)                                    #
        # ------------------------------------------------------------------ #
        cls.company_b = cls.env["res.partner"].create(
            {"name": "Company B", "is_company": True}
        )
        cls.portal_user_b = cls.env["res.users"].create(
            {
                "name": "Portal User B",
                "login": "portal_user_b@test.com",
                "email": "portal_user_b@test.com",
                "group_ids": [
                    Command.link(cls.env.ref("base.group_portal").id),
                ],
                "partner_id": cls.env["res.partner"]
                .create(
                    {
                        "name": "Portal User B",
                        "parent_id": cls.company_b.id,
                        "type": "contact",
                    }
                )
                .id,
            }
        )

        # Delivery address belonging to Company A.
        cls.delivery_addr_a = cls.env["res.partner"].create(
            {
                "name": "Delivery A1",
                "type": "delivery",
                "parent_id": cls.company_a.id,
                "street": "1 Test Street",
                "city": "Mumbai",
                "country_id": cls.env.ref("base.in").id,
                "is_portal_delivery": True,
            }
        )

        # Delivery address belonging to Company B.
        cls.delivery_addr_b = cls.env["res.partner"].create(
            {
                "name": "Delivery B1",
                "type": "delivery",
                "parent_id": cls.company_b.id,
                "street": "2 Other Street",
                "city": "Delhi",
                "country_id": cls.env.ref("base.in").id,
                "is_portal_delivery": True,
            }
        )

        # Product for sale orders.
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu"}
        )

    # ------------------------------------------------------------------ #
    # AC1, AC2, AC3: Delivery address creation and retrieval              #
    # ------------------------------------------------------------------ #

    def test_delivery_address_creation(self):
        """AC1-AC3: Created address has type='delivery', correct parent and flag."""
        addr = self.env["res.partner"].create(
            {
                "name": "New Portal Delivery",
                "type": "delivery",
                "parent_id": self.company_a.id,
                "is_portal_delivery": True,
            }
        )
        self.assertEqual(addr.type, "delivery", "Address type must be 'delivery'.")
        self.assertEqual(
            addr.parent_id,
            self.company_a,
            "Parent must be the commercial partner.",
        )
        self.assertTrue(addr.is_portal_delivery, "is_portal_delivery flag must be set.")
        self.assertEqual(
            addr.commercial_partner_id,
            self.company_a,
            "commercial_partner_id must resolve to the company.",
        )

    def test_get_portal_delivery_addresses(self):
        """AC1: _get_portal_delivery_addresses returns company's deliveries."""
        addrs = self.company_a._get_portal_delivery_addresses()
        self.assertIn(self.delivery_addr_a, addrs, "Company A address must be listed.")
        self.assertNotIn(
            self.delivery_addr_b, addrs, "Company B address must NOT be listed."
        )

    def test_can_be_edited_by_current_customer_own_address(self):
        """AC3: User A can edit their own delivery address."""
        result = self.delivery_addr_a.with_user(
            self.portal_user_a
        )._can_be_edited_by_current_customer()
        self.assertTrue(
            result, "User A must be able to edit their own delivery address."
        )

    def test_can_be_edited_by_current_customer_other_tenant(self):
        """AC6: User A cannot edit User B's delivery address."""
        result = self.delivery_addr_b.with_user(
            self.portal_user_a
        )._can_be_edited_by_current_customer()
        self.assertFalse(
            result, "User A must NOT be able to edit User B's delivery address."
        )

    # ------------------------------------------------------------------ #
    # AC4, AC5: Shipping address update on sale orders                    #
    # ------------------------------------------------------------------ #

    def _make_sale_order(self, partner, state="draft"):
        """Create a minimal sale order for the given partner."""
        order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        if state == "sent":
            order.action_quotation_sent()
        return order

    def test_sale_order_shipping_selection_draft(self):
        """AC4: Shipping address can be updated on a draft order."""
        order = self._make_sale_order(self.company_a)
        order.action_update_portal_shipping_address(self.delivery_addr_a)
        self.assertEqual(
            order.partner_shipping_id,
            self.delivery_addr_a,
            "Shipping address must be updated on draft order.",
        )

    def test_sale_order_shipping_selection_sent(self):
        """AC4: Shipping address can be updated on a sent quotation."""
        order = self._make_sale_order(self.company_a, state="sent")
        order.action_update_portal_shipping_address(self.delivery_addr_a)
        self.assertEqual(
            order.partner_shipping_id,
            self.delivery_addr_a,
            "Shipping address must be updated on sent quotation.",
        )

    def test_sale_order_state_protection_confirmed(self):
        """AC5: Shipping address cannot be changed on a confirmed sale order."""
        order = self._make_sale_order(self.company_a)
        order.action_confirm()
        with self.assertRaises(UserError):
            order.action_update_portal_shipping_address(self.delivery_addr_a)

    def test_sale_order_state_protection_cancelled(self):
        """AC5: Shipping address cannot be changed on a cancelled sale order."""
        order = self._make_sale_order(self.company_a)
        order._action_cancel()
        with self.assertRaises(UserError):
            order.action_update_portal_shipping_address(self.delivery_addr_a)

    def test_sale_order_cross_tenant_address_rejected(self):
        """AC6: User A order rejects User B address (raises AccessError)."""
        order = self._make_sale_order(self.company_a)
        with self.assertRaises(AccessError):
            order.action_update_portal_shipping_address(self.delivery_addr_b)

    # ------------------------------------------------------------------ #
    # AC7: Address archiving                                              #
    # ------------------------------------------------------------------ #

    def test_address_archive(self):
        """AC7: Archiving a secondary delivery address hides it from active lists."""
        addr = self.env["res.partner"].create(
            {
                "name": "To-Be-Archived Delivery",
                "type": "delivery",
                "parent_id": self.company_a.id,
                "is_portal_delivery": True,
            }
        )
        # Verify visible before archive.
        addrs_before = self.company_a._get_portal_delivery_addresses()
        self.assertIn(addr, addrs_before)

        addr.active = False  # Archive.

        # Verify hidden after archive.
        addrs_after = self.company_a._get_portal_delivery_addresses()
        self.assertNotIn(
            addr,
            addrs_after,
            "Archived address must not appear in active delivery address list.",
        )

    def test_commercial_partner_cannot_be_archived_via_delivery(self):
        """AC7, DECISION 2: The commercial/main partner is not a delivery type,
        so our helper method cannot be abused to archive it."""
        # company_a is a company (is_company=True), so type='contact' by default.
        addrs = self.company_a._get_portal_delivery_addresses()
        self.assertNotIn(
            self.company_a,
            addrs,
            "Commercial partner must not appear in delivery address list.",
        )
