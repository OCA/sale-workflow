# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import ast

from odoo.tests import TransactionCase


class TestSaleOrderAddressFilter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create(
            {"name": "Customer", "is_company": True}
        )
        cls.customer_contact = cls.env["res.partner"].create(
            {"name": "Customer Contact", "parent_id": cls.customer.id}
        )
        cls.other_partner = cls.env["res.partner"].create({"name": "Other Partner"})

    def test_address_domain_only_customer_contacts(self):
        """With the toggle on, only the customer's contacts are selectable."""
        order = self.env["sale.order"].create({"partner_id": self.customer.id})
        domain = ast.literal_eval(order.address_domain)
        self.assertIn(
            ("commercial_partner_id", "=", self.customer.commercial_partner_id.id),
            domain,
        )
        partners = self.env["res.partner"].search(domain)
        self.assertIn(self.customer, partners)
        self.assertIn(self.customer_contact, partners)
        self.assertNotIn(self.other_partner, partners)

    def test_address_domain_toggle_off(self):
        """With the toggle off, any partner of the company is selectable."""
        order = self.env["sale.order"].create(
            {"partner_id": self.customer.id, "only_customer_addresses": False}
        )
        self.assertEqual(
            ast.literal_eval(order.address_domain),
            [
                "|",
                ("company_id", "=", False),
                ("company_id", "=", order.company_id.id),
            ],
        )
        partners = self.env["res.partner"].search(
            ast.literal_eval(order.address_domain)
        )
        self.assertIn(self.other_partner, partners)

    def test_address_domain_respects_company(self):
        """Contacts of another company are never selectable."""
        other_company = self.env["res.company"].create({"name": "Other Company"})
        other_company_partner = self.env["res.partner"].create(
            {"name": "Other Company Partner", "company_id": other_company.id}
        )
        order = self.env["sale.order"].create(
            {"partner_id": self.customer.id, "only_customer_addresses": False}
        )
        partners = self.env["res.partner"].search(
            ast.literal_eval(order.address_domain)
        )
        self.assertNotIn(other_company_partner, partners)
