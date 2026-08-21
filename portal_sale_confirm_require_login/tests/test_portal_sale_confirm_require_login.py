# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from urllib.parse import urlparse

from odoo import Command
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestPortalSaleConfirmRequireLogin(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Portal Sale Confirm Require Login",
                "email": "pscrl@test.com",
                "street": "Test Street",
                "city": "Test City",
                "zip": "12345",
                "country_id": cls.env.ref("base.es").id,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.order._portal_ensure_token()
        cls.portal_url = (
            f"/my/orders/{cls.order.id}?access_token={cls.order.access_token}"
        )
        cls.env["ir.config_parameter"].sudo().set_param(
            "portal_sale_confirm_require_login.portal_sale_access_login_required",
            True,
        )

    def test_existing_user_redirected_to_login(self):
        self.env["res.users"].with_context(no_reset_password=True).create(
            {
                "name": self.partner.name,
                "login": self.partner.email,
                "email": self.partner.email,
                "partner_id": self.partner.id,
                "group_ids": [Command.set([self.env.ref("base.group_portal").id])],
            }
        )
        response = self.url_open(self.portal_url, allow_redirects=False)
        self.assertEqual(
            urlparse(response.headers["Location"]).path,
            "/web/login",
        )

    def test_partner_without_user_redirected_to_signup(self):
        response = self.url_open(self.portal_url, allow_redirects=False)
        self.assertEqual(
            urlparse(response.headers["Location"]).path,
            "/web/signup",
        )

    def test_missing_partner_data_requires_completion(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "portal_sale_confirm_require_login.portal_sale_access_login_required",
            False,
        )
        self.order.require_signature = True
        response = self.url_open(self.portal_url)
        self.assertIn(
            f"/my/account?order_id={self.order.id}",
            response.text,
        )
