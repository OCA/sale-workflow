#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import pathlib

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestAcceptTerms(HttpCase):
    def browser_js(self, url_path, code, ready="", **kwargs):
        # Workaround: some Chrome versions don't create chrome_debug.log even
        # with --enable-logging. Odoo's _wait_code_ok reads this file eagerly
        # (not lazily), so it raises FileNotFoundError before the tour result
        # is determined. Pre-creating the file avoids this.
        self.start_browser()
        log_path = pathlib.Path(self.browser.user_data_dir, "chrome_debug.log")
        if not log_path.exists():
            log_path.touch()
        return super().browser_js(url_path, code, ready=ready, **kwargs)

    def test_tour_accep_terms(self):
        """If a configured product has `website_hide_price` enabled,
        the price is hidden and the message is shown.
        """
        portal_user = self.env.ref("base.demo_user0")

        order = self.env["sale.order"].create(
            {
                "partner_id": portal_user.partner_id.id,
                "require_signature": True,
                "portal_accept_terms": "Something",
            }
        )

        self.start_tour(
            order.get_portal_url(),
            "portal_sale_accept_terms.accept_terms",
            login=portal_user.login,
        )
