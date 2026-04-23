# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"].with_context(test_propagation=True)
        cls.salesperson = cls.env["res.users"].create(
            {
                "name": "Test Salesperson",
                "login": "sales@test.com",
            }
        )
        cls.team = cls.env["crm.team"].create({"name": "Sales Team A"})
        cls.parent_partner = cls.partner_model.create(
            {
                "name": "Company A",
                "company_type": "company",
                "user_id": cls.salesperson.id,
                "team_id": cls.team.id,
            }
        )
        cls.child_contact = cls.partner_model.create(
            {
                "name": "Child Contact",
                "parent_id": cls.parent_partner.id,
            }
        )

    def test_propagate_user_id(self):
        """Test that changing user_id propagates to child contacts"""
        new_salesperson = self.env["res.users"].create(
            {
                "name": "New Salesperson",
                "login": "new_sales@test.com",
            }
        )
        self.parent_partner.write({"user_id": new_salesperson.id})
        self.assertEqual(self.child_contact.user_id, new_salesperson)

    def test_propagate_team_id(self):
        """Test that changing team_id propagates to child contacts"""
        new_team = self.env["crm.team"].create({"name": "Sales Team B"})
        self.parent_partner.write({"team_id": new_team.id})
        self.assertEqual(self.child_contact.team_id, new_team)

    def test_inherit_team_id_on_creation(self):
        """Test that a new contact inherits team_id from parent"""
        new_contact = self.partner_model.create(
            {
                "name": "New Contact",
                "parent_id": self.parent_partner.id,
            }
        )
        self.assertEqual(new_contact.team_id, self.team)

    def test_change_parent_id_updates_team_id(self):
        """Test that changing parent_id updates team_id if not set"""
        new_parent_partner = self.partner_model.create(
            {
                "name": "Company B",
                "company_type": "company",
                "team_id": self.team.id,
            }
        )
        self.child_contact.write({"parent_id": new_parent_partner.id})
        self.assertEqual(self.child_contact.team_id, self.team)
