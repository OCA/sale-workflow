# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase


class TestSaleContactType(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_child_ordering = cls.env["res.partner"].create(
            {"name": "Test child ordering", "type": "ordering"}
        )
        cls.partner_parent = cls.env["res.partner"].create(
            {"name": "Test parent", "company_type": "company"}
        )

    def test_compute_has_ordering_contact_child(self):
        self.assertFalse(self.partner_parent.has_ordering_contact_child)
        self.partner_parent.write({"child_ids": [(4, self.partner_child_ordering.id)]})
        self.assertTrue(self.partner_parent.has_ordering_contact_child)
