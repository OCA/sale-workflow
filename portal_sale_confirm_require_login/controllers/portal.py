# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from werkzeug.urls import url_encode

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.sale.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):
    def _get_signup_url(self, partner, redirect_url):
        partner = partner.sudo()
        partner.signup_prepare()
        query_string = url_encode(
            {"token": partner.signup_token, "redirect": redirect_url}
        )
        return f"/web/signup?{query_string}"

    def _get_mandatory_fields(self):
        mandatory_fields = super()._get_mandatory_fields()
        partner = request.env.user.partner_id
        if partner.can_edit_vat() and "vat" not in mandatory_fields:
            mandatory_fields.append("vat")
        return mandatory_fields

    @http.route()
    def account(self, redirect=None, **post):
        partner = request.env.user.partner_id
        country_id = post.get("country_id")
        if partner.can_edit_country() and country_id and country_id != "False":
            # The standard portal account flow overwrites posted country_id with the
            # partner's current country when VAT cannot be edited. If the country is
            # still empty but allowed to be completed, write it first so the standard
            # flow can continue without overriding the whole account() method.
            partner.sudo().write({"country_id": int(country_id)})
        response = super().account(redirect=redirect, **post)
        if response.qcontext:
            response.qcontext["partner_can_edit_country"] = partner.can_edit_country()
        return response

    @http.route()
    def portal_order_page(
        self,
        order_id,
        report_type=None,
        access_token=None,
        message=False,
        download=False,
        downpayment=None,
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
                downpayment=downpayment,
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
                downpayment=downpayment,
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
                downpayment=downpayment,
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
                downpayment=downpayment,
                **kw,
            )
        try:
            order_sudo = self._document_check_access(
                "sale.order", order_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        partner = order_sudo.partner_id
        redirect_url = f"/my/orders/{order_id}?access_token={access_token}"
        user = partner.user_ids.filtered("active")[:1]
        if user:
            qs = url_encode({"login": user.login or "", "redirect": redirect_url})
            return request.redirect(f"/web/login?{qs}")
        return request.redirect(self._get_signup_url(partner, redirect_url))

    def details_form_validate(self, data, partner_creation=False):
        error, error_message = super().details_form_validate(
            data, partner_creation=partner_creation
        )
        partner = request.env.user.partner_id
        if data.get("country_id") == "False" and partner.can_edit_country():
            error["country_id"] = "missing"
            required_msg = _("Some required fields are empty.")
            if required_msg not in error_message:
                error_message.append(required_msg)
        return error, error_message
