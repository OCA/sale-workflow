# Copyright 2016-2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common


class TestCommon(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.team = cls.env["crm.team"].create({"name": "Test channel"})
        cls.team2 = cls.env["crm.team"].create({"name": "Test channel 2"})
        cls.user = cls.env["res.users"].create(
            {
                "login": "sales_team_security",
                "name": "Test sales_team_security user",
                "groups_id": [(4, cls.env.ref("sales_team.group_sale_salesman").id)],
            }
        )
        cls.crm_team_member = cls.env["crm.team.member"].create(
            {
                "user_id": cls.user.id,
                "crm_team_id": cls.team.id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "team_id": cls.team.id}
        )
        cls.partner_child_1 = cls.env["res.partner"].create(
            {"name": "Child 1", "parent_id": cls.partner.id}
        )
        cls.partner_child_2 = cls.env["res.partner"].create(
            {"name": "Child 2", "parent_id": cls.partner.id, "type": "invoice"}
        )
        cls.user2 = cls.env["res.users"].create(
            {
                "login": "sales_team_security2",
                "name": "Test sales_team_security user 2",
                "groups_id": [(4, cls.env.ref("sales_team.group_sale_salesman").id)],
            }
        )
        cls.crm_team_member2 = cls.env["crm.team.member"].create(
            {
                "user_id": cls.user2.id,
                "crm_team_id": cls.team.id,
            }
        )
        cls.check_permission_subscribe = False

    def _check_permission(self, salesman, team, expected):
        self.record.write(
            {
                "user_id": salesman.id if salesman else salesman,
                "team_id": team.id if team else team,
            }
        )
        domain = [("id", "=", self.record.id)]
        if (
            self.check_permission_subscribe
        ):  # Force unsubscription for not interfering with real test
            self.record.message_subscribe(partner_ids=self.user.partner_id.ids)
        else:
            self.record.message_unsubscribe(partner_ids=self.user.partner_id.ids)
        obj = self.env[self.record._name].with_user(self.user)
        self.assertEqual(bool(obj.search(domain)), expected)

    def _check_whole_permission_set(self, extra_checks=True):
        self._check_permission(False, False, True)
        self._check_permission(self.user, False, True)
        self._check_permission(self.user2, False, False)
        self._check_permission(False, self.team, True)
        if extra_checks:
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
        if extra_checks:
            self._check_permission(False, self.team2, False)
        self._check_permission(self.user, self.team, True)
        if self.record._name == "res.partner":
            self.check_permission_subscribe = True
            self._check_permission(self.user, self.team2, True)
            self.check_permission_subscribe = False
        else:
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
        if extra_checks:
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
