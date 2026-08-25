# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from werkzeug.urls import url_encode

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.sale.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):
    def _get_signup_url(self, partner, redirect_url):
        partner = partner.sudo()
        partner.signup_prepare()
        query_string = url_encode(
            {"token": partner._generate_signup_token(), "redirect": redirect_url}
        )
        return f"/web/signup?{query_string}"

    def _get_mandatory_billing_address_fields(self, country_sudo):
        mandatory_fields = super()._get_mandatory_billing_address_fields(country_sudo)
        partner = request.env.user.partner_id
        if partner.can_edit_vat():
            mandatory_fields.add("vat")
        return mandatory_fields

    @http.route()
    def portal_order_page(
        self,
        order_id,
        report_type=None,
        access_token=None,
        message=False,
        download=False,
        payment_amount=None,
        amount_selection=None,
        **kw,
    ):
        # If disabled, public users can access the portal sale document page.
        # Login is still enforced on protected actions.
        login_required = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "portal_sale_confirm_require_login.portal_sale_access_login_required",
            )
        )
        login_required = login_required == "True"
        if not login_required:
            return super().portal_order_page(
                order_id,
                report_type=report_type,
                access_token=access_token,
                message=message,
                download=download,
                payment_amount=payment_amount,
                amount_selection=amount_selection,
                **kw,
            )
        # Do not interfere with report rendering / downloads
        if report_type in ("html", "pdf", "text"):
            return super().portal_order_page(
                order_id,
                report_type=report_type,
                access_token=access_token,
                message=message,
                download=download,
                payment_amount=payment_amount,
                amount_selection=amount_selection,
                **kw,
            )
        # Avoid breaking link previewers (WhatsApp/Slack/etc.)
        if request.httprequest.headers.get("Odoo-Link-Preview") == "True":
            return super().portal_order_page(
                order_id,
                report_type=report_type,
                access_token=access_token,
                message=message,
                download=download,
                payment_amount=payment_amount,
                amount_selection=amount_selection,
                **kw,
            )
        # Force login/signup when accessing a quotation via access_token.
        # Only apply when user is public and access is via token
        if not (request.env.user._is_public() and access_token):
            return super().portal_order_page(
                order_id,
                report_type=report_type,
                access_token=access_token,
                message=message,
                download=download,
                payment_amount=payment_amount,
                amount_selection=amount_selection,
                **kw,
            )
        try:
            order_sudo = self._document_check_access(
                "sale.order", order_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        partner = order_sudo.partner_id
        redirect_params = {"access_token": access_token}
        if payment_amount is not None:
            redirect_params["payment_amount"] = payment_amount
        if amount_selection is not None:
            redirect_params["amount_selection"] = amount_selection
        redirect_url = f"/my/orders/{order_id}?{url_encode(redirect_params)}"
        user = partner.user_ids.filtered("active")[:1]
        if user:
            qs = url_encode({"login": user.login or "", "redirect": redirect_url})
            return request.redirect(f"/web/login?{qs}")
        return request.redirect(self._get_signup_url(partner, redirect_url))
