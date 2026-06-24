# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import HttpCase


class TestPortalSaleOrderSearch(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env["res.partner"]
        cls.company = Partner.create({"name": "Wonka Company", "is_company": True})
        cls.alice = Partner.create({"name": "Alice Apple", "parent_id": cls.company.id})
        cls.bob = Partner.create({"name": "Bob Banana", "parent_id": cls.company.id})
        # The portal user is attached to the company (not a single contact) so
        # that both contacts' orders stay visible regardless of the portal
        # visibility rule in effect: the standard rule filters on the
        # commercial partner, while portal_sale_personal_data_only (auto
        # installed) filters on the user's own partner. Both resolve to the
        # company here, so the test does not depend on which one is active.
        cls.portal_user = cls.env["res.users"].create(
            {
                "name": "Wonka Portal",
                "login": "wonka_portal",
                "password": "wonka_portal",
                "partner_id": cls.company.id,
                "groups_id": [Command.link(cls.env.ref("base.group_portal").id)],
            }
        )
        SaleOrder = cls.env["sale.order"]
        cls.order_alice = SaleOrder.create(
            {"partner_id": cls.alice.id, "client_order_ref": "REF-ALICE"}
        )
        cls.order_bob = SaleOrder.create(
            {"partner_id": cls.bob.id, "client_order_ref": "REF-BOB"}
        )
        cls.order_alice.message_subscribe(partner_ids=cls.alice.ids)
        cls.order_bob.message_subscribe(partner_ids=cls.bob.ids)
        (cls.order_alice + cls.order_bob).write({"state": "sale"})

    def _open_orders(self, search=None, search_in=None):
        """Authenticate as the portal user and return the /my/orders body."""
        self.authenticate("wonka_portal", "wonka_portal")
        url = "/my/orders"
        if search is not None:
            url += "?search=%s&search_in=%s" % (search, search_in)
        return self.url_open(url).text

    def test_search_by_name(self):
        body = self._open_orders(self.order_alice.name, "name")
        self.assertIn(self.order_alice.name, body)
        self.assertNotIn(self.order_bob.name, body)

    def test_search_by_ref(self):
        body = self._open_orders("REF-BOB", "ref")
        self.assertIn(self.order_bob.name, body)
        self.assertNotIn(self.order_alice.name, body)

    def test_search_by_partner_contact(self):
        # "Customer" matches the order's contact name only.
        body = self._open_orders("Bob Banana", "partner")
        self.assertIn(self.order_bob.name, body)
        self.assertNotIn(self.order_alice.name, body)

    def test_search_by_company_matches_both_contacts(self):
        # "Customer Company" matches the commercial partner, so both
        # sibling contacts' orders are returned.
        body = self._open_orders("Wonka", "company")
        self.assertIn(self.order_alice.name, body)
        self.assertIn(self.order_bob.name, body)

    def test_search_partner_does_not_match_company(self):
        # The company name must not be matched by the contact-only search.
        body = self._open_orders("Wonka", "partner")
        self.assertNotIn(self.order_alice.name, body)
        self.assertNotIn(self.order_bob.name, body)

    def test_search_all(self):
        # "All" matches reference, contact and company.
        body = self._open_orders("Wonka", "all")
        self.assertIn(self.order_alice.name, body)
        self.assertIn(self.order_bob.name, body)
        body = self._open_orders("REF-ALICE", "all")
        self.assertIn(self.order_alice.name, body)
        self.assertNotIn(self.order_bob.name, body)
