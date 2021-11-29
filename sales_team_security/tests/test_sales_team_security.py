# Copyright 2016-2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from lxml import etree

from ..hooks import post_init_hook
from .common import TestCommon


class TestSalesTeamSecurity(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_partner = cls.user.partner_id
        cls.user2_partner = cls.user2.partner_id
        cls.record = cls.partner

    def test_onchange_parent_id(self):
        contact = self.env["res.partner"].create(
            {"name": "Test contact", "parent_id": self.partner.id}
        )
        contact._onchange_parent_id_sales_team_security()
        self.assertEqual(contact.team_id, self.team)

    def test_onchange_user_id(self):
        contact = self.env["res.partner"].create(
            {
                "name": "Test contact",
                "user_id": self.user.id,
            }
        )
        contact._onchange_user_id_sales_team_security()
        self.assertEqual(contact.team_id, self.team)

    def test_assign_contacts_team(self):
        contact = self.env["res.partner"].create(
            {"name": "Test contact", "parent_id": self.partner.id, "team_id": False}
        )
        post_init_hook(self.env.cr, self.env.registry)
        contact.refresh()
        self.assertEqual(contact.team_id, self.partner.team_id)

    def test_change_user_id_partner(self):
        self.partner.write({"user_id": self.user.id})
        self.assertIn(self.user_partner, self.partner.message_partner_ids)
        self.assertNotIn(self.user_partner, self.partner_child_1.message_partner_ids)
        self.assertIn(self.user_partner, self.partner_child_2.message_partner_ids)
        # Change salesman
        self.partner.write({"user_id": self.user2.id})
        self.assertNotIn(self.user_partner, self.partner.message_partner_ids)
        self.assertIn(self.user2_partner, self.partner.message_partner_ids)
        self.assertNotIn(self.user_partner, self.partner_child_2.message_partner_ids)
        self.assertIn(self.user2_partner, self.partner_child_2.message_partner_ids)

    def test_change_user_id_partner_child_1(self):
        self.partner_child_1.write({"user_id": self.user.id})
        self.assertIn(self.user_partner, self.partner.message_partner_ids)
        self.assertIn(self.user_partner, self.partner_child_2.message_partner_ids)
        # Change salesman
        self.partner_child_1.write({"user_id": self.user2.id})
        self.assertNotIn(self.user_partner, self.partner.message_partner_ids)
        self.assertIn(self.user2_partner, self.partner.message_partner_ids)
        self.assertNotIn(self.user_partner, self.partner_child_2.message_partner_ids)
        self.assertIn(self.user2_partner, self.partner_child_2.message_partner_ids)

    def test_partner_fields_view_get(self):
        res = self.env["res.partner"].fields_view_get(
            view_id=self.ref("base.view_partner_form")
        )
        eview = etree.fromstring(res["arch"])
        xml_fields = eview.xpath("//field[@name='child_ids']")
        self.assertTrue(xml_fields)
        self.assertTrue("default_team_id" in xml_fields[0].get("context", ""))

    def test_partner_permissions(self):
        self._check_whole_permission_set()

    def test_partner_permissions_subscription(self):
        self.check_permission_subscribe = True
        self._check_permission(self.user2, False, True)

    def test_partner_permissions_own_partner(self):
        self.user.partner_id.write({"user_id": self.user2.id})
        domain = [("id", "in", self.user.partner_id.ids)]
        Partner = self.env["res.partner"].with_user(self.user)
        # Make sure the acces is not due to the subscription
        self.partner.message_unsubscribe(partner_ids=self.user.partner_id.ids)
        self.assertEqual(bool(Partner.search(domain)), True)
