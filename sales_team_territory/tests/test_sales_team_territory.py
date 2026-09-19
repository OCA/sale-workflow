# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSalesTeamTerritory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mexico = cls.env.ref("base.mx")
        cls.guatemala = cls.env.ref("base.gt")
        cls.jalisco = cls.env.ref("base.state_mx_jal")
        cls.sonora = cls.env.ref("base.state_mx_son")
        cls.leader_1, cls.leader_2 = cls.env["res.users"].create(
            [
                {"name": "Leader 1", "login": "leader_1"},
                {"name": "Leader 2", "login": "leader_2"},
            ]
        )
        cls.team_1 = cls.env["crm.team"].create(
            {
                "name": "Zone 1",
                "user_id": cls.leader_1.id,
                "state_ids": [(6, 0, cls.jalisco.ids)],
                "country_ids": [(6, 0, cls.guatemala.ids)],
            }
        )
        cls.team_2 = cls.env["crm.team"].create(
            {
                "name": "Zone 2",
                "user_id": cls.leader_2.id,
                "country_ids": [(6, 0, cls.mexico.ids)],
            }
        )

    def _create_partner(self, **vals):
        vals.setdefault("name", "Test partner")
        return self.env["res.partner"].create(vals)

    def test_assign_by_state(self):
        partner = self._create_partner(
            country_id=self.mexico.id, state_id=self.jalisco.id
        )
        self.assertEqual(partner.team_id, self.team_1)
        self.assertEqual(partner.user_id, self.leader_1)

    def test_assign_by_country(self):
        partner = self._create_partner(country_id=self.guatemala.id)
        self.assertEqual(partner.team_id, self.team_1)
        partner = self._create_partner(
            country_id=self.mexico.id, state_id=self.sonora.id
        )
        self.assertEqual(partner.team_id, self.team_2)

    def test_keep_salesperson_and_manual_team(self):
        partner = self._create_partner(
            user_id=self.leader_2.id, country_id=self.guatemala.id
        )
        self.assertEqual(partner.team_id, self.team_1)
        self.assertEqual(partner.user_id, self.leader_2)
        partner = self._create_partner(team_id=self.team_2.id)
        self.assertEqual(partner.team_id, self.team_2)
        partner.country_id = self.guatemala
        self.assertEqual(partner.team_id, self.team_1)

    def test_child_follows_parent(self):
        company = self._create_partner(
            is_company=True, country_id=self.mexico.id, state_id=self.jalisco.id
        )
        contact = self._create_partner(parent_id=company.id, type="contact")
        self.assertEqual(contact.team_id, self.team_1)
        self.assertEqual(contact.user_id, self.leader_1)
        delivery = self._create_partner(
            parent_id=company.id,
            type="delivery",
            country_id=self.mexico.id,
            state_id=self.sonora.id,
        )
        self.assertEqual(delivery.team_id, self.team_2)

    def test_overlap_constraint(self):
        with self.assertRaises(ValidationError):
            self.team_2.state_ids = self.jalisco
        with self.assertRaises(ValidationError):
            self.env["crm.team"].create(
                {"name": "Zone 3", "country_ids": [(6, 0, self.mexico.ids)]}
            )

    def test_assign_existing_partners(self):
        partner = self._create_partner(
            country_id=self.mexico.id, state_id=self.sonora.id
        )
        self.assertEqual(partner.team_id, self.team_2)
        self.team_1.state_ids += self.sonora
        self.assertEqual(partner.team_id, self.team_2)
        self.team_1.action_assign_territory_partners()
        self.assertEqual(partner.team_id, self.team_1)

    def test_other_company_team_not_matched(self):
        company = self.env["res.company"].create({"name": "Other company"})
        self.team_2.country_ids = False
        self.env["crm.team"].create(
            {
                "name": "Zone 3",
                "company_id": company.id,
                "country_ids": [(6, 0, self.mexico.ids)],
            }
        )
        partner = self._create_partner(
            country_id=self.mexico.id, state_id=self.sonora.id
        )
        self.assertFalse(partner.team_id)
        partner.company_id = company
        self.assertEqual(partner.team_id.name, "Zone 3")
