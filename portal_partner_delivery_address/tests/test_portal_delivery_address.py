# Copyright 2026 Tohid Pathan (Allied Vision Technologies Pvt. Ltd.)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import MagicMock, PropertyMock, patch

from werkzeug.exceptions import Forbidden

from odoo.exceptions import AccessError, UserError
from odoo.fields import Command
from odoo.tests import TransactionCase, tagged

from ..controllers.portal_delivery_address import DeliveryAddressPortal


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

    def test_can_be_edited_by_current_customer_no_partner(self):
        """Line 55-56 of res_partner.py: Return False if no current partner resolved."""
        addr = self.env["res.partner"].create(
            {
                "name": "Test No Partner",
                "type": "delivery",
                "parent_id": self.company_a.id,
            }
        )
        with patch.object(
            type(self.env["res.partner"]),
            "_get_current_partner",
            return_value=False,
        ):
            self.assertFalse(addr._can_be_edited_by_current_customer())

    # ------------------------------------------------------------------ #
    # Controller Unit Tests: 100% Deterministic Branch Coverage          #
    # ------------------------------------------------------------------ #

    def test_validate_address_values_delivery_vat(self):
        """Validate address values strips vat and empty message for delivery."""
        controller = DeliveryAddressPortal()
        with patch(
            "odoo.addons.portal_partner_delivery_address.controllers.portal_delivery_address.request",
            new=MagicMock(),
        ) as mock_request:
            mock_request.env = self.env
            with patch(
                "odoo.addons.portal.controllers.portal.CustomerPortal._validate_address_values",
                return_value=(
                    {"vat"},
                    {"vat"},
                    [self.env._("Some required fields are empty.")],
                ),
            ):
                invalid, missing, msgs = controller._validate_address_values(
                    address_values={},
                    partner_sudo=self.env["res.partner"],
                    address_type="delivery",
                    use_delivery_as_billing=False,
                    required_fields="vat",
                )
                self.assertNotIn("vat", invalid)
                self.assertNotIn("vat", missing)
                self.assertFalse(msgs)

    def test_controller_create_or_update_address_callback_order_id_and_token(self):
        """Extract order_id and access_token from callback URL when omitted in form."""
        controller = DeliveryAddressPortal()
        order = self.env["sale.order"].create(
            {
                "partner_id": self.company_a.id,
                "partner_invoice_id": self.company_a.id,
                "partner_shipping_id": self.company_a.id,
                "state": "sent",
            }
        )
        order._portal_ensure_token()
        delivery_partner = self.env["res.partner"].create(
            {
                "name": "Unit Delivery",
                "type": "delivery",
                "parent_id": self.company_a.id,
                "is_portal_delivery": True,
            }
        )
        with patch(
            "odoo.addons.portal_partner_delivery_address.controllers.portal_delivery_address.request",
            new=MagicMock(),
        ) as mock_request:
            mock_request.env = self.env(user=self.portal_user_a)
            with (
                patch(
                    "odoo.addons.portal.controllers.portal.CustomerPortal._create_or_update_address",
                    return_value=(delivery_partner, {}),
                ),
                patch.object(
                    DeliveryAddressPortal,
                    "_document_check_access",
                    return_value=order,
                ),
            ):
                callback_url = (
                    f"/my/orders/{order.id}?access_token={order.access_token}"
                )
                res_partner, feedback = controller._create_or_update_address(
                    partner_sudo=False,
                    address_type="delivery",
                    callback=callback_url,
                )
                self.assertEqual(res_partner, delivery_partner)
                self.assertEqual(order.partner_shipping_id, delivery_partner)

    def test_controller_create_or_update_address_exception_handled(self):
        """Address creation proceeds even if order auto-assignment fails."""
        controller = DeliveryAddressPortal()
        delivery_partner = self.env["res.partner"].create(
            {
                "name": "Unit Delivery Ex",
                "type": "delivery",
                "parent_id": self.company_a.id,
                "is_portal_delivery": True,
            }
        )
        with patch(
            "odoo.addons.portal_partner_delivery_address.controllers.portal_delivery_address.request",
            new=MagicMock(),
        ) as mock_request:
            mock_request.env = self.env(user=self.portal_user_a)
            with patch(
                "odoo.addons.portal.controllers.portal.CustomerPortal._create_or_update_address",
                return_value=(delivery_partner, {}),
            ):
                with patch.object(
                    DeliveryAddressPortal,
                    "_document_check_access",
                    side_effect=AccessError("Forbidden"),
                ):
                    res_partner, feedback = controller._create_or_update_address(
                        partner_sudo=False,
                        address_type="delivery",
                        order_id="123",
                    )
                    self.assertEqual(res_partner, delivery_partner)

    def test_controller_update_shipping_address_missing_or_forbidden_order(self):
        """Missing or inaccessible order raises Forbidden."""
        controller = DeliveryAddressPortal()
        with patch.object(
            DeliveryAddressPortal,
            "_document_check_access",
            side_effect=AccessError("Forbidden"),
        ):
            with self.assertRaises(Forbidden):
                controller.portal_update_shipping_address(order_id=999)

    def test_controller_update_shipping_address_cross_tenant_order(self):
        """Cross-tenant order update raises Forbidden."""
        controller = DeliveryAddressPortal()
        order_b = self.env["sale.order"].create(
            {
                "partner_id": self.company_b.id,
                "partner_invoice_id": self.company_b.id,
                "partner_shipping_id": self.company_b.id,
            }
        )
        with patch(
            "odoo.addons.portal_partner_delivery_address.controllers.portal_delivery_address.request",
            new=MagicMock(),
        ) as mock_request:
            mock_request.env = self.env(user=self.portal_user_a)
            with patch.object(
                DeliveryAddressPortal,
                "_document_check_access",
                return_value=order_b,
            ):
                with self.assertRaises(Forbidden):
                    controller.portal_update_shipping_address(order_id=order_b.id)

    def test_controller_update_shipping_address_invalid_partner_id(self):
        """Invalid shipping partner id returns HTTP 400 JSON."""
        controller = DeliveryAddressPortal()
        order = self.env["sale.order"].create(
            {
                "partner_id": self.company_a.id,
                "partner_invoice_id": self.company_a.id,
                "partner_shipping_id": self.company_a.id,
            }
        )
        with patch(
            "odoo.addons.portal_partner_delivery_address.controllers.portal_delivery_address.request",
            new=MagicMock(),
        ) as mock_request:
            mock_request.env = self.env(user=self.portal_user_a)
            mock_request.make_json_response.side_effect = lambda data, status=200: (
                data,
                status,
            )
            with patch.object(
                DeliveryAddressPortal,
                "_document_check_access",
                return_value=order,
            ):
                res = controller.portal_update_shipping_address(
                    order_id=order.id, shipping_partner_id="invalid"
                )
                self.assertEqual(
                    res,
                    (
                        {"error": self.env._("Invalid shipping address.")},
                        400,
                    ),
                )

    def test_controller_update_shipping_address_nonexistent_partner(self):
        """Non-existent shipping partner raises Forbidden."""
        controller = DeliveryAddressPortal()
        order = self.env["sale.order"].create(
            {
                "partner_id": self.company_a.id,
                "partner_invoice_id": self.company_a.id,
                "partner_shipping_id": self.company_a.id,
            }
        )
        with patch(
            "odoo.addons.portal_partner_delivery_address.controllers.portal_delivery_address.request",
            new=MagicMock(),
        ) as mock_request:
            mock_request.env = self.env(user=self.portal_user_a)
            with patch.object(
                DeliveryAddressPortal,
                "_document_check_access",
                return_value=order,
            ):
                with self.assertRaises(Forbidden):
                    controller.portal_update_shipping_address(
                        order_id=order.id, shipping_partner_id="999999"
                    )

    def test_controller_update_shipping_address_cross_tenant_address(self):
        """Shipping partner belonging to another company raises Forbidden."""
        controller = DeliveryAddressPortal()
        order = self.env["sale.order"].create(
            {
                "partner_id": self.company_a.id,
                "partner_invoice_id": self.company_a.id,
                "partner_shipping_id": self.company_a.id,
            }
        )
        addr_b = self.env["res.partner"].create(
            {
                "name": "Delivery B",
                "type": "delivery",
                "parent_id": self.company_b.id,
            }
        )
        with patch(
            "odoo.addons.portal_partner_delivery_address.controllers.portal_delivery_address.request",
            new=MagicMock(),
        ) as mock_request:
            mock_request.env = self.env(user=self.portal_user_a)
            with patch.object(
                DeliveryAddressPortal,
                "_document_check_access",
                return_value=order,
            ):
                with self.assertRaises(Forbidden):
                    controller.portal_update_shipping_address(
                        order_id=order.id, shipping_partner_id=str(addr_b.id)
                    )

    def test_controller_update_shipping_address_partner_access_error(self):
        """AccessError on shipping partner commercial partner raises Forbidden."""
        controller = DeliveryAddressPortal()
        order = self.env["sale.order"].create(
            {
                "partner_id": self.company_a.id,
                "partner_invoice_id": self.company_a.id,
                "partner_shipping_id": self.company_a.id,
            }
        )
        addr_a = self.env["res.partner"].create(
            {
                "name": "Delivery A",
                "type": "delivery",
                "parent_id": self.company_a.id,
            }
        )
        with patch(
            "odoo.addons.portal_partner_delivery_address.controllers.portal_delivery_address.request",
            new=MagicMock(),
        ) as mock_request:
            mock_request.env = self.env(user=self.portal_user_a)
            with patch.object(
                DeliveryAddressPortal,
                "_document_check_access",
                return_value=order,
            ):
                with patch.object(
                    type(addr_a),
                    "commercial_partner_id",
                    new_callable=PropertyMock,
                    side_effect=AccessError("Forbidden"),
                ):
                    with self.assertRaises(Forbidden):
                        controller.portal_update_shipping_address(
                            order_id=order.id,
                            shipping_partner_id=str(addr_a.id),
                        )

    def test_controller_update_shipping_address_user_error_json_and_raise(self):
        """UserError returns 400 for JSON and re-raises for standard requests."""
        controller = DeliveryAddressPortal()
        order = self.env["sale.order"].create(
            {
                "partner_id": self.company_a.id,
                "partner_invoice_id": self.company_a.id,
                "partner_shipping_id": self.company_a.id,
            }
        )
        addr_a = self.env["res.partner"].create(
            {
                "name": "Delivery A",
                "type": "delivery",
                "parent_id": self.company_a.id,
            }
        )
        with patch(
            "odoo.addons.portal_partner_delivery_address.controllers.portal_delivery_address.request",
            new=MagicMock(),
        ) as mock_request:
            mock_request.env = self.env(user=self.portal_user_a)
            mock_request.httprequest.headers = {"Accept": "application/json"}
            mock_request.make_json_response.side_effect = lambda data, status=200: (
                data,
                status,
            )
            with patch.object(
                DeliveryAddressPortal,
                "_document_check_access",
                return_value=order,
            ):
                with patch.object(
                    type(order),
                    "action_update_portal_shipping_address",
                    side_effect=UserError("Order locked"),
                ):
                    res = controller.portal_update_shipping_address(
                        order_id=order.id, shipping_partner_id=str(addr_a.id)
                    )
                    self.assertEqual(res, ({"error": "Order locked"}, 400))

                    # Non-JSON Accept re-raises UserError
                    mock_request.httprequest.headers = {"Accept": "text/html"}
                    with self.assertRaises(UserError):
                        controller.portal_update_shipping_address(
                            order_id=order.id,
                            shipping_partner_id=str(addr_a.id),
                        )

    def test_controller_update_shipping_address_model_access_error(self):
        """AccessError during address update raises Forbidden."""
        controller = DeliveryAddressPortal()
        order = self.env["sale.order"].create(
            {
                "partner_id": self.company_a.id,
                "partner_invoice_id": self.company_a.id,
                "partner_shipping_id": self.company_a.id,
            }
        )
        addr_a = self.env["res.partner"].create(
            {
                "name": "Delivery A",
                "type": "delivery",
                "parent_id": self.company_a.id,
            }
        )
        with patch(
            "odoo.addons.portal_partner_delivery_address.controllers.portal_delivery_address.request",
            new=MagicMock(),
        ) as mock_request:
            mock_request.env = self.env(user=self.portal_user_a)
            with patch.object(
                DeliveryAddressPortal,
                "_document_check_access",
                return_value=order,
            ):
                with patch.object(
                    type(order),
                    "action_update_portal_shipping_address",
                    side_effect=AccessError("Forbidden"),
                ):
                    with self.assertRaises(Forbidden):
                        controller.portal_update_shipping_address(
                            order_id=order.id,
                            shipping_partner_id=str(addr_a.id),
                        )

    def test_controller_update_shipping_address_success_json_and_html(self):
        """Successful shipping update returns JSON redirect or HTTP redirect."""
        controller = DeliveryAddressPortal()
        order = self.env["sale.order"].create(
            {
                "partner_id": self.company_a.id,
                "partner_invoice_id": self.company_a.id,
                "partner_shipping_id": self.company_a.id,
                "state": "sent",
            }
        )
        addr_a = self.env["res.partner"].create(
            {
                "name": "Delivery A",
                "type": "delivery",
                "parent_id": self.company_a.id,
                "is_portal_delivery": True,
            }
        )
        with patch(
            "odoo.addons.portal_partner_delivery_address.controllers.portal_delivery_address.request",
            new=MagicMock(),
        ) as mock_request:
            mock_request.env = self.env(user=self.portal_user_a)
            mock_request.httprequest.headers = {"Accept": "application/json"}
            mock_request.make_json_response.side_effect = lambda data, status=200: (
                data,
                status,
            )
            mock_request.redirect.side_effect = lambda url: f"REDIRECT:{url}"
            with patch.object(
                DeliveryAddressPortal,
                "_document_check_access",
                return_value=order,
            ):
                res_json = controller.portal_update_shipping_address(
                    order_id=order.id, shipping_partner_id=str(addr_a.id)
                )
                self.assertEqual(
                    res_json,
                    (
                        {
                            "success": True,
                            "redirect": order.get_portal_url(),
                        },
                        200,
                    ),
                )

                mock_request.httprequest.headers = {"Accept": "text/html"}
                res_html = controller.portal_update_shipping_address(
                    order_id=order.id, shipping_partner_id=str(addr_a.id)
                )
                self.assertEqual(res_html, f"REDIRECT:{order.get_portal_url()}")

    def test_controller_sale_order_get_page_view_values_public_user(self):
        """Public user gets empty portal delivery addresses and no change right."""
        controller = DeliveryAddressPortal()
        order = self.env["sale.order"].create(
            {
                "partner_id": self.company_a.id,
                "partner_invoice_id": self.company_a.id,
                "partner_shipping_id": self.company_a.id,
            }
        )
        public_user = self.env.ref("base.public_user")
        with patch(
            "odoo.addons.portal_partner_delivery_address.controllers.portal_delivery_address.request",
            new=MagicMock(),
        ) as mock_request:
            mock_request.env = self.env(user=public_user)
            with patch(
                "odoo.addons.sale.controllers.portal.CustomerPortal._sale_order_get_page_view_values",
                return_value={},
            ):
                values = controller._sale_order_get_page_view_values(
                    order, access_token=None, values={}, history_session_key=""
                )
                self.assertFalse(values["portal_delivery_addresses"])
                self.assertFalse(values["can_change_shipping"])
