# Copyright 2016-2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from lxml import etree

from odoo.tests import common

from ..hooks import post_init_hook


class TestSalesTeamSecurity(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.team = cls.env["crm.team"].create({"name": "Test channel"})
        cls.team2 = cls.env["crm.team"].create({"name": "Test channel 2"})
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "team_id": cls.team.id}
        )
        cls.partner_child_1 = cls.env["res.partner"].create(
            {"name": "Child 1", "parent_id": cls.partner.id}
        )
        cls.partner_child_2 = cls.env["res.partner"].create(
            {"name": "Child 2", "parent_id": cls.partner.id, "type": "invoice"}
        )
        cls.user = cls.env["res.users"].create(
            {
                "login": "sales_team_security",
                "name": "Test sales_team_security user",
                "groups_id": [(4, cls.env.ref("sales_team.group_sale_salesman").id)],
                "sale_team_id": cls.team.id,
            }
        )
        cls.user_partner = cls.user.partner_id
        cls.user2 = cls.env["res.users"].create(
            {
                "login": "sales_team_security2",
                "name": "Test sales_team_security user 2",
                "groups_id": [(4, cls.env.ref("sales_team.group_sale_salesman").id)],
                "sale_team_id": cls.team.id,
            }
        )
        cls.user2_partner = cls.user2.partner_id

    def _is_module_installed(self, name):
        return bool(
            self.env["ir.module.module"].search(
                [("name", "=", name), ("state", "=", "installed")]
            )
        )

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

    def _check_permission(self, salesman, team, expected, subscribe=False):
        self.partner.write(
            {
                "user_id": salesman.id if salesman else salesman,
                "team_id": team.id if team else team,
            }
        )
        domain = [("id", "in", self.partner.ids)]
        Partner = self.env["res.partner"].with_user(self.user)
        if subscribe:  # Force unsubscription for not interfering with real test
            self.partner.message_subscribe(partner_ids=self.user.partner_id.ids)
        else:
            self.partner.message_unsubscribe(partner_ids=self.user.partner_id.ids)
        self.assertEqual(bool(Partner.search(domain)), expected)

    def test_partner_permissions(self):
        self._check_permission(False, False, True)
        self._check_permission(self.user, False, True)
        self._check_permission(self.user2, False, False)
        self._check_permission(False, self.team, True)
        self._check_permission(False, self.team2, False)
        self._check_permission(self.user, self.team, True)
        self._check_permission(self.user, self.team2, True)
        self._check_permission(self.user2, self.team2, False)
        self._check_permission(self.user2, self.team, False)
        # Add to group "Team manager"
        self.user.groups_id = [
            (4, self.env.ref("sales_team_security.group_sale_team_manager").id)
        ]
        self._check_permission(False, False, True)
        self._check_permission(self.user, False, True)
        self._check_permission(self.user2, False, True)
        self._check_permission(False, self.team, True)
        self._check_permission(False, self.team2, False)
        self._check_permission(self.user, self.team, True)
        self._check_permission(self.user, self.team2, True)
        self._check_permission(self.user2, self.team2, False)
        self._check_permission(self.user2, self.team, True)
        # Add to group "See all leads"
        self.user.groups_id = [
            (4, self.env.ref("sales_team.group_sale_salesman_all_leads").id)
        ]
        self._check_permission(False, False, True)
        self._check_permission(self.user, False, True)
        self._check_permission(self.user2, False, True)
        self._check_permission(False, self.team, True)
        self._check_permission(False, self.team2, True)
        self._check_permission(self.user, self.team, True)
        self._check_permission(self.user, self.team2, True)
        self._check_permission(self.user2, self.team2, True)
        self._check_permission(self.user2, self.team, True)
        # Regular internal user
        self.user.groups_id = [(6, 0, [self.env.ref("base.group_user").id])]
        self._check_permission(False, False, True)
        self._check_permission(self.user, False, True)
        self._check_permission(self.user2, False, True)
        self._check_permission(False, self.team, True)
        self._check_permission(False, self.team2, True)
        self._check_permission(self.user, self.team, True)
        self._check_permission(self.user, self.team2, True)
        self._check_permission(self.user2, self.team2, True)
        self._check_permission(self.user2, self.team, True)

    def test_partner_permissions_subscription(self):
        self._check_permission(self.user2, False, True, subscribe=True)

    def test_partner_permissions_own_partner(self):
        self.user.partner_id.write({"user_id": self.user2.id})
        domain = [("id", "in", self.user.partner_id.ids)]
        Partner = self.env["res.partner"].with_user(self.user)
        # Make sure the acces is not due to the subscription
        self.partner.message_unsubscribe(partner_ids=self.user.partner_id.ids)
        self.assertEqual(bool(Partner.search(domain)), True)
