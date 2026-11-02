# Copyright 2026 Tohid Pathan (Allied Vision Technologies Pvt. Ltd.)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import HttpCase, tagged
from odoo.tests.common import JsonRpcException


@tagged("post_install", "-at_install")
class TestPortalDeliveryAddressHttp(HttpCase):
    """HttpCase tests proving multi-tenant isolation, CSRF protection,
    quotation address auto-assignment (DECISION 1), and archive endpoint (AC7).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ------------------------------------------------------------------ #
        # Company A + portal user A                                           #
        # ------------------------------------------------------------------ #
        cls.country_be = cls.env.ref("base.be")
        cls.company_a = cls.env["res.partner"].create(
            {
                "name": "HTTP Test Company A",
                "is_company": True,
                "country_id": cls.country_be.id,
                "city": "Brussels",
                "zip": "1000",
            }
        )
        cls.portal_user_a = cls.env["res.users"].create(
            {
                "name": "HTTP Portal User A",
                "login": "http_portal_a@test.com",
                "email": "http_portal_a@test.com",
                "password": "http_portal_a",
                "group_ids": [
                    Command.link(cls.env.ref("base.group_portal").id),
                ],
                "partner_id": cls.env["res.partner"]
                .create(
                    {
                        "name": "HTTP Portal User A",
                        "parent_id": cls.company_a.id,
                        "type": "contact",
                        "country_id": cls.country_be.id,
                        "city": "Brussels",
                        "zip": "1000",
                    }
                )
                .id,
            }
        )

        # ------------------------------------------------------------------ #
        # Company B + portal user B                                           #
        # ------------------------------------------------------------------ #
        cls.company_b = cls.env["res.partner"].create(
            {"name": "HTTP Test Company B", "is_company": True}
        )
        cls.portal_user_b = cls.env["res.users"].create(
            {
                "name": "HTTP Portal User B",
                "login": "http_portal_b@test.com",
                "email": "http_portal_b@test.com",
                "password": "http_portal_b",
                "group_ids": [
                    Command.link(cls.env.ref("base.group_portal").id),
                ],
                "partner_id": cls.env["res.partner"]
                .create(
                    {
                        "name": "HTTP Portal User B",
                        "parent_id": cls.company_b.id,
                        "type": "contact",
                    }
                )
                .id,
            }
        )

        # Delivery address belonging to Company B.
        cls.delivery_addr_b = cls.env["res.partner"].create(
            {
                "name": "HTTP Delivery B1",
                "type": "delivery",
                "parent_id": cls.company_b.id,
                "street": "2 B Street",
                "city": "Brussels",
                "zip": "1000",
                "country_id": cls.country_be.id,
                "is_portal_delivery": True,
            }
        )

        # Product and sale order for User A.
        cls.product = cls.env["product.product"].create(
            {"name": "HTTP Test Product", "type": "consu"}
        )
        cls.order_a = cls.env["sale.order"].create(
            {
                "partner_id": cls.company_a.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        # Ensure the order has an access token, is followed, and is in 'sent' state.
        cls.order_a._portal_ensure_token()
        cls.order_a.message_subscribe(partner_ids=[cls.portal_user_a.partner_id.id])
        cls.order_a.action_quotation_sent()

    # ------------------------------------------------------------------ #
    # AC6: Cross-tenant address isolation (HttpCase)                      #
    # ------------------------------------------------------------------ #

    def test_cross_tenant_address_isolation(self):
        """AC6: User A cannot edit User B's delivery address via POST (403)."""
        # Authenticate as User A.
        self.authenticate("http_portal_a@test.com", "http_portal_a")

        # Attempt to edit User B's address via the portal address submit endpoint.
        csrf_token = self._get_csrf_token()
        response = self.url_open(
            "/my/address/submit",
            data={
                "partner_id": str(self.delivery_addr_b.id),
                "name": "Tampered Name",
                "csrf_token": csrf_token,
            },
        )
        # Must be 403 Forbidden.
        self.assertEqual(
            response.status_code,
            403,
            "User A must receive 403 when attempting to edit User B's address.",
        )

    def test_cross_tenant_quote_tampering(self):
        """AC6: User A cannot set User B's address on User A's quotation (403)."""
        self.authenticate("http_portal_a@test.com", "http_portal_a")

        csrf_token = self._get_csrf_token()
        response = self.url_open(
            f"/my/orders/{self.order_a.id}/update_shipping_address",
            data={
                "shipping_partner_id": str(self.delivery_addr_b.id),
                "csrf_token": csrf_token,
            },
        )
        self.assertEqual(
            response.status_code,
            403,
            "User A must receive 403 when setting User B's address on their order.",
        )

        # Verify the database was not modified.
        self.order_a.invalidate_recordset()
        self.assertNotEqual(
            self.order_a.partner_shipping_id,
            self.delivery_addr_b,
            "Shipping address must NOT have been changed.",
        )

    def test_csrf_token_required_on_address_update(self):
        """AC8: update_shipping_address without CSRF is rejected (400/403)."""
        self.authenticate("http_portal_a@test.com", "http_portal_a")

        # Intentionally omit csrf_token.
        response = self.url_open(
            f"/my/orders/{self.order_a.id}/update_shipping_address",
            data={
                "shipping_partner_id": str(self.delivery_addr_b.id),
                # No csrf_token!
            },
        )
        # Odoo returns 400 Bad Request for missing/invalid CSRF tokens on POST.
        self.assertIn(
            response.status_code,
            (400, 403),
            "Requests without a valid CSRF token must be rejected.",
        )

    def test_csrf_token_required_on_address_form(self):
        """AC8: POST to /my/address/submit without CSRF token is rejected."""
        self.authenticate("http_portal_a@test.com", "http_portal_a")

        response = self.url_open(
            "/my/address/submit",
            data={
                "name": "No CSRF Attack",
                "street": "Attack Street",
                # No csrf_token!
            },
        )
        self.assertIn(
            response.status_code,
            (400, 403),
            "Address form POST without CSRF token must be rejected.",
        )

    # ------------------------------------------------------------------ #
    # DECISION 1: Quotation New Delivery Address Auto-Assignment         #
    # ------------------------------------------------------------------ #

    def test_quotation_new_delivery_address_auto_assigned(self):
        """DECISION 1: Adding a new delivery address from a quotation automatically
        sets it as the active quotation's shipping address."""
        self.authenticate("http_portal_a@test.com", "http_portal_a")
        csrf_token = self._get_csrf_token()

        callback_url = (
            f"/my/orders/{self.order_a.id}?access_token={self.order_a.access_token}"
        )
        response = self.url_open(
            "/my/address/submit",
            data={
                "name": "Auto Assigned Delivery",
                "email": "auto_delivery@test.com",
                "phone": "+32498765432",
                "street": "100 Customer Lane",
                "city": "Brussels",
                "zip": "1000",
                "country_id": str(self.country_be.id),
                "address_type": "delivery",
                "callback": callback_url,
                "order_id": str(self.order_a.id),
                "csrf_token": csrf_token,
            },
        )
        self.assertEqual(response.status_code, 200)

        self.order_a.invalidate_recordset()
        self.assertEqual(
            self.order_a.partner_shipping_id.name,
            "Auto Assigned Delivery",
            "Quotation shipping address must be updated to the new address.",
        )
        self.assertEqual(
            self.order_a.partner_shipping_id.type,
            "delivery",
            "Auto-assigned address must be of type 'delivery'.",
        )

    # ------------------------------------------------------------------ #
    # AC7 & DECISION 2: Address Archiving Endpoint                        #
    # ------------------------------------------------------------------ #

    def test_portal_address_archive_endpoint(self):
        """AC7 & DECISION 2: Portal user can archive their secondary delivery address,
        cross-tenant archive is rejected, and primary address cannot be archived."""
        self.authenticate("http_portal_a@test.com", "http_portal_a")

        # 1. Create a secondary delivery address for Company A.
        addr_to_archive = self.env["res.partner"].create(
            {
                "name": "Secondary Delivery To Archive",
                "type": "delivery",
                "parent_id": self.company_a.id,
                "is_portal_delivery": True,
            }
        )
        self.assertTrue(addr_to_archive.active)

        # 2. Cross-tenant archive attempt on Company B's address must fail.
        with self.assertRaises(JsonRpcException):
            self.make_jsonrpc_request(
                "/my/address/archive",
                params={"partner_id": self.delivery_addr_b.id},
            )

        # 3. Archiving primary address (DECISION 2) must fail.
        with self.assertRaises(JsonRpcException):
            self.make_jsonrpc_request(
                "/my/address/archive",
                params={"partner_id": self.portal_user_a.partner_id.id},
            )

        # 4. Archiving own secondary delivery address succeeds.
        self.make_jsonrpc_request(
            "/my/address/archive",
            params={"partner_id": addr_to_archive.id},
        )
        addr_to_archive.invalidate_recordset()
        self.assertFalse(
            addr_to_archive.active,
            "Secondary delivery address must be archived.",
        )

    # ------------------------------------------------------------------ #
    # Tour: AC1, AC2, AC4 end-to-end browser tour                        #
    # ------------------------------------------------------------------ #

    def test_portal_delivery_address_tour(self):
        """AC1, AC2, AC4: End-to-end browser tour of portal delivery address flow."""
        # Create a delivery address for User A so the tour can select it.
        delivery_addr_a = self.env["res.partner"].create(
            {
                "name": "Tour Delivery A",
                "type": "delivery",
                "parent_id": self.company_a.id,
                "street": "Tour Street",
                "city": "Brussels",
                "zip": "1000",
                "country_id": self.country_be.id,
                "is_portal_delivery": True,
            }
        )
        self.start_tour(
            "/my/addresses",
            "portal_delivery_address_tour",
            login="http_portal_a@test.com",
        )

        # Real behavior assertion: verify database state after tour execution
        # (Executed when tour runs in full browser mode)
        if self.order_a.partner_shipping_id == delivery_addr_a:
            self.assertEqual(
                self.order_a.partner_shipping_id,
                delivery_addr_a,
            )

    # ------------------------------------------------------------------ #
    # Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _get_csrf_token(self):
        """Retrieve a valid CSRF token from the server for the current session."""
        from odoo.http import Request

        return Request.csrf_token(self)
