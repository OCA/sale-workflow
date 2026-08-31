# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestResPartner(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"].with_context(test_propagation=True)
        cls.salesperson = new_test_user(
            cls.env,
            name="Test Salesperson",
            login="sales@test.com",
        )
        cls.new_salesperson = new_test_user(
            cls.env,
            name="New Salesperson",
            login="new_sales@test.com",
        )
        cls.other_salesperson = new_test_user(
            cls.env,
            name="Other Salesperson",
            login="other_sales@test.com",
        )
        cls.parent_partner = cls.partner_model.create(
            {
                "name": "Company A",
                "is_company": True,
                "user_id": cls.salesperson.id,
            }
        )
        cls.child_contact = cls.partner_model.create(
            {
                "name": "Child Contact",
                "parent_id": cls.parent_partner.id,
            }
        )

    def test_inherit_user_id_on_creation(self):
        """A contact created under a company gets its salesperson (done by
        Odoo core, but the module relies on it)."""
        self.assertEqual(self.child_contact.user_id, self.salesperson)

    def test_propagate_user_id(self):
        """Changing the salesperson propagates to the contacts having the
        previous one."""
        self.parent_partner.write({"user_id": self.new_salesperson.id})
        self.assertEqual(self.child_contact.user_id, self.new_salesperson)

    def test_propagate_user_id_empty_child(self):
        """Changing the salesperson propagates to the contacts having none."""
        self.child_contact.write({"user_id": False})
        self.parent_partner.write({"user_id": self.new_salesperson.id})
        self.assertEqual(self.child_contact.user_id, self.new_salesperson)

    def test_no_propagate_user_id_own_salesperson(self):
        """Contacts with their own salesperson are not touched."""
        self.child_contact.write({"user_id": self.other_salesperson.id})
        self.parent_partner.write({"user_id": self.new_salesperson.id})
        self.assertEqual(self.child_contact.user_id, self.other_salesperson)

    def test_propagate_user_id_hierarchy(self):
        """The propagation goes down the whole contacts hierarchy."""
        grand_child_contact = self.partner_model.create(
            {
                "name": "Grand Child Contact",
                "parent_id": self.child_contact.id,
            }
        )
        self.assertEqual(grand_child_contact.user_id, self.salesperson)
        self.parent_partner.write({"user_id": self.new_salesperson.id})
        self.assertEqual(grand_child_contact.user_id, self.new_salesperson)

    def test_no_propagation_without_context(self):
        """Propagation is disabled during other modules tests."""
        parent = self.env["res.partner"].browse(self.parent_partner.id)
        parent.write({"user_id": self.new_salesperson.id})
        self.assertEqual(self.child_contact.user_id, self.salesperson)
