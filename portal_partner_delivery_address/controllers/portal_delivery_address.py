# Copyright 2026 Tohid Pathan (Allied Vision Technologies Pvt. Ltd.)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class DeliveryAddressPortal(CustomerPortal):
    """Extend the core portal controller with delivery address management.

    All endpoints follow OCA security guidelines:
    - Ownership verification before any sudo() escalation.
    - CSRF tokens enforced automatically by Odoo on every POST.
    - 403 Forbidden raised immediately on ownership mismatch.
    """

    # ------------------------------------------------------------------ #
    # Section 1: Address creation & Quotation auto-assignment (DECISION 1)#
    # ------------------------------------------------------------------ #

    def _complete_address_values(
        self, address_values, address_type, use_delivery_as_billing, **form_data
    ):
        """Override to force type='delivery' and correct parent_id.

        When a portal user creates a delivery address, we must guarantee:
        - ``type`` is ``'delivery'`` regardless of the form value.
        - ``parent_id`` is the commercial partner, so the address appears as a
          child of the company, not an orphan.
        - ``is_portal_delivery`` is set to ``True`` for auditing.

        :param dict address_values: Mutable address values about to be saved.
        :param str address_type: 'delivery' or 'billing'.
        :param bool use_delivery_as_billing: Whether this doubles as billing.
        """
        res = super()._complete_address_values(
            address_values, address_type, use_delivery_as_billing, **form_data
        )
        if address_type == "delivery":
            current_partner = request.env["res.partner"]._get_current_partner(
                **form_data
            )
            commercial_partner = current_partner.commercial_partner_id
            address_values["type"] = "delivery"
            if commercial_partner.active:
                address_values["parent_id"] = commercial_partner.id
            address_values["is_portal_delivery"] = True
        return res

    def _create_or_update_address(
        self,
        partner_sudo,
        address_type="billing",
        use_delivery_as_billing=False,
        callback="/my/addresses",
        required_fields=False,
        verify_address_values=True,
        **form_data,
    ):
        """Override to auto-set new delivery address on quotation (DECISION 1)."""
        is_new = not partner_sudo
        created_or_updated_partner, feedback_dict = super()._create_or_update_address(
            partner_sudo,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            required_fields=required_fields,
            verify_address_values=verify_address_values,
            **form_data,
        )
        if (
            is_new
            and address_type == "delivery"
            and created_or_updated_partner
            and not feedback_dict.get("messages")
        ):
            order_id = form_data.get("order_id")
            if not order_id and callback and "/my/orders/" in callback:
                match = re.search(r"/my/orders/(\d+)", callback)
                if match:
                    order_id = match.group(1)
            if order_id and str(order_id).isdigit():
                try:
                    access_token = form_data.get("access_token")
                    if not access_token and callback and "access_token=" in callback:
                        token_match = re.search(
                            r"access_token=([a-zA-Z0-9_-]+)", callback
                        )
                        if token_match:
                            access_token = token_match.group(1)
                    order_sudo = self._document_check_access(
                        "sale.order", int(order_id), access_token=access_token
                    )
                    current_partner = request.env.user.partner_id
                    if (
                        order_sudo.partner_id.commercial_partner_id
                        == current_partner.commercial_partner_id
                        and order_sudo.state in ("draft", "sent")
                    ):
                        order_sudo.action_update_portal_shipping_address(
                            created_or_updated_partner
                        )
                except Exception as err:
                    # Do not block address creation if quotation update fails
                    _logger.debug("Quotation address auto-assignment skipped: %s", err)
        return created_or_updated_partner, feedback_dict

    # ------------------------------------------------------------------ #
    # Section 2: POST /my/orders/<order_id>/update_shipping_address       #
    # ------------------------------------------------------------------ #

    @http.route(
        "/my/orders/<int:order_id>/update_shipping_address",
        type="http",
        methods=["POST"],
        auth="user",
        website=True,
        csrf=True,
    )
    def portal_update_shipping_address(self, order_id, shipping_partner_id=None, **kw):
        """Update the shipping address on a draft/sent quotation.

        Security contract (defence in depth):
        1. The sale order must belong to the current portal user's commercial partner.
        2. The proposed shipping address must share the same commercial partner.
        3. The order must be in draft/sent state.
        Any failure raises ``Forbidden`` → HTTP 403.

        CSRF is automatically enforced by Odoo on every POST route when
        ``csrf=True`` (the default).  Specified explicitly here for clarity.

        :param int order_id: The sale order ID from the URL.
        :param str shipping_partner_id: The proposed shipping partner ID from the form.
        :return: JSON response with either a redirect URL or an error message.
        :rtype: werkzeug.wrappers.Response
        """
        # ------------------------------------------------------------------
        # Step 1: Locate and authorise the sale order.
        # ------------------------------------------------------------------
        try:
            order_sudo = self._document_check_access("sale.order", order_id)
        except (AccessError, MissingError) as err:
            raise Forbidden() from err

        current_partner = request.env.user.partner_id
        # Ownership guard: sale order's commercial partner must match the user.
        if (
            order_sudo.partner_id.commercial_partner_id
            != current_partner.commercial_partner_id
        ):
            raise Forbidden()

        # ------------------------------------------------------------------
        # Step 2: Resolve and authorise proposed shipping address without
        #         premature sudo().
        # ------------------------------------------------------------------
        if not shipping_partner_id or not str(shipping_partner_id).isdigit():
            return request.make_json_response(
                {"error": request.env._("Invalid shipping address.")}, status=400
            )

        try:
            shipping_partner = request.env["res.partner"].browse(
                int(shipping_partner_id)
            )
            if not shipping_partner.exists():
                raise Forbidden()

            # Address ownership guard: must share the same commercial partner.
            if (
                shipping_partner.commercial_partner_id
                != current_partner.commercial_partner_id
            ):
                raise Forbidden()
        except AccessError as err:
            raise Forbidden() from err

        # sudo: ownership verified above; sudo passed to model method to ensure
        # necessary relational fields are accessible in portal context.
        shipping_partner_sudo = shipping_partner.sudo()

        # ------------------------------------------------------------------
        # Step 3: Delegate the actual write to the model method, which also
        #         validates state and re-checks commercial partner.
        # ------------------------------------------------------------------
        try:
            order_sudo.action_update_portal_shipping_address(shipping_partner_sudo)
        except UserError as exc:
            if "application/json" in request.httprequest.headers.get("Accept", ""):
                return request.make_json_response({"error": str(exc)}, status=400)
            raise
        except (AccessError, Forbidden) as err:
            raise Forbidden() from err

        if "application/json" in request.httprequest.headers.get("Accept", ""):
            return request.make_json_response(
                {"success": True, "redirect": order_sudo.get_portal_url()}
            )
        return request.redirect(order_sudo.get_portal_url())

    # ------------------------------------------------------------------ #
    # Section 3: GET /my/orders/<order_id> – inject delivery addresses    #
    # ------------------------------------------------------------------ #

    def _sale_order_get_page_view_values(
        self, order_sudo, access_token, values, history_session_key, **kwargs
    ):
        """Inject portal delivery addresses into the quotation page context.

        The delivery addresses are loaded for the current portal user so the
        template can render a dropdown/selector for draft/sent orders.

        :return: Enriched values dict.
        :rtype: dict
        """
        values = super()._sale_order_get_page_view_values(
            order_sudo, access_token, values, history_session_key, **kwargs
        )
        if not request.env.user._is_public():
            current_partner = request.env.user.partner_id
            delivery_addresses = (
                current_partner.commercial_partner_id._get_portal_delivery_addresses()
            )
            # sudo: delivery addresses belong to current user's commercial partner;
            # sudo is used to ensure contact fields render in portal templates.
            values["portal_delivery_addresses"] = delivery_addresses.sudo()
            values["can_change_shipping"] = order_sudo.state in (
                "draft",
                "sent",
            )
        else:
            values["portal_delivery_addresses"] = request.env["res.partner"]
            values["can_change_shipping"] = False
        return values
