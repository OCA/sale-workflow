# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestDropshipDeliveryAddress(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner1 = cls.env["res.partner"].create({"name": "Test Partner 1"})
        cls.child_1 = cls.env["res.partner"].create(
            {"name": "Child 1", "parent_id": cls.partner1.id, "type": "delivery"}
        )

    def test_dropship_delivery_address(self):
        self.assertIn(self.partner1.name, self.child_1.display_name)
        self.child_1.is_dropship_address = True
        self.child_1._compute_display_name()
        self.assertNotIn(self.partner1.name, self.child_1.display_name)
