# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestSalePartnerSaleContactRequired(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create(
            {"name": "Test Customer", "is_company": True}
        )
        cls.contact = cls.env["res.partner"].create(
            {"name": "Test Contact", "parent_id": cls.customer.id}
        )

    def test_field_is_required(self):
        field = self.env["sale.order"]._fields["sale_contact_partner_id"]
        self.assertTrue(field.required)
        # Invoices keep the contact optional.
        move_field = self.env["account.move"]._fields["sale_contact_partner_id"]
        self.assertFalse(move_field.required)

    def test_order_with_sale_contact(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "sale_contact_partner_id": self.contact.id,
            }
        )
        self.assertEqual(order.sale_contact_partner_id, self.contact)

    @mute_logger("odoo.sql_db")
    def test_order_without_sale_contact(self):
        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            self.env["sale.order"].create({"partner_id": self.customer.id})
            self.env.flush_all()
