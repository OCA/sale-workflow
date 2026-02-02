#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestAcceptTerms(HttpCase):
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
