# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.sale_order_model = cls.env["sale.order"]
        company = cls.env.company
        company.keep_name_so = False
        cls.company1 = cls.env["res.company"].create(
            {"name": "Test Company 1", "keep_name_so": False}
        )
        # Creating our own sequences for the company to make tests easier
        cls.sequence_so = cls.env["ir.sequence"].create(
            {
                "name": "Sales Order",
                "prefix": "SO/",
                "padding": 5,
                "code": "sale.order",
                "company_id": cls.company1.id,
            }
        )
        cls.sequence_sq = cls.env["ir.sequence"].create(
            {
                "name": "Sales Quotation",
                "prefix": "SQ/",
                "padding": 3,
                "code": "sale.quotation",
                "company_id": cls.company1.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        name = cls.sequence_sq._next_do()
        cls.order_company1 = cls.env["sale.order"].create(
            {
                "name": name,
                "partner_id": cls.partner.id,
                "company_id": cls.company1.id,
            }
        )

    def test_create_without_name(self):
        order = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "company_id": self.company1.id,
            }
        )
        # It needs to assign a name based on the sale.quotation sequence
        self.assertRegex(order.name, "SQ/")
        self.assertTrue(self.sequence_sq.name_fits_sequence(order.name))

    def test_create_with_specific_name(self):
        order = self.sale_order_model.create(
            {
                "name": "CustomName",
                "partner_id": self.partner.id,
                "company_id": self.company1.id,
            }
        )
        # It needs to keep the custom name
        self.assertEqual(order.name, "CustomName")

    def test_create_with_dynamic_prefix(self):
        self.sequence_sq.write({"prefix": "SQ/%(year)s/"})
        order = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "company_id": self.company1.id,
            }
        )
        # It needs to assign a name based on the sale.quotation sequence
        # This checks that name_fits_sequence works even for dynamic prefixes
        self.assertRegex(order.name, r"SQ/(19|20|21)\d{2}/")
        self.assertTrue(self.sequence_sq.name_fits_sequence(order.name))

    def test_sequence_assignment(self):
        next_name = self.sequence_so.get_next_char(self.sequence_so.number_next_actual)
        self.order_company1.action_confirm()
        # It needs to detect that this needs a new name
        # from the sale.order sequence and assign it
        self.assertEqual(next_name, self.order_company1.name)

    def test_sequence_assignment_negative(self):
        order = self.sale_order_model.create(
            {
                "name": "CustomName",
                "partner_id": self.partner.id,
                "company_id": self.company1.id,
            }
        )
        order.action_confirm()
        # It needs to preserve the custom name during the confirmation
        self.assertEqual(order.name, "CustomName")

    def test_sequence_assignment_negative_regex(self):
        # Create a sale order with an *almost* correct name
        name = "SQ/002 - Copy"
        order = self.sale_order_model.create(
            {
                "name": name,
                "partner_id": self.partner.id,
                "company_id": self.company1.id,
            }
        )
        order.action_confirm()
        # It needs to preserve the custom name during the confirmation
        # since while it shares the prefix, it does not fit the full regex
        self.assertEqual(order.name, name)

    def test_sequence_assignment_multicompany(self):
        new_company = self.env["res.company"].create(
            {"name": "Test Company 2", "keep_name_so": False}
        )
        base_sequence = self.env["ir.sequence"].search(
            [
                ("code", "=", "sale.order"),
                ("company_id", "=", False),
            ]
        )
        # Set the company-free sequence to have a very
        # different prefix than the company_1 sequence
        base_sequence.write({"prefix": "ORD/%(y)s-%(month)s/"})
        next_name = base_sequence.get_next_char(base_sequence.number_next_actual)
        order = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "company_id": new_company.id,
            }
        )
        # Confirm orders belonging to multiple companies at once
        (self.order_company1 | order).action_confirm()
        # Check that the new name belongs to the base_sequence,
        # not the company_1 sequence
        self.assertEqual(order.name, next_name)
        self.assertTrue(base_sequence.name_fits_sequence(order.name))
        self.assertFalse(self.sequence_so.name_fits_sequence(order.name))

    def test_confirm_no_origin(self):
        old_name = self.order_company1.name
        self.order_company1.action_confirm()
        # The old name of the quotation is found in the origin
        self.assertEqual(self.order_company1.origin, old_name)

    def test_confirm_with_origin(self):
        origin = "origin"
        order1 = self.sale_order_model.create(
            {
                "origin": origin,
                "partner_id": self.partner.id,
                "company_id": self.company1.id,
            }
        )
        quotation1_name = order1.name
        order1.action_confirm()

        # The origin of the quotation is appended to the old name
        self.assertEqual(order1.origin, ", ".join([origin, quotation1_name]))

    def test_enumeration(self):
        order1 = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "company_id": self.company1.id,
            }
        )
        quotation1_name = order1.name
        order2 = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "company_id": self.company1.id,
            }
        )
        quotation2_name = order2.name

        # Check that the Quotation created first has the lower index
        self.assertLess(quotation1_name, quotation2_name)

        order2.action_confirm()
        order1.action_confirm()

        # Check that the Order confirmed first has the lower index
        self.assertLess(order2.name, order1.name)

    def test_error_confirmation_sequence(self):
        order = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "state": "sale",
                "company_id": self.company1.id,
            }
        )
        next_name = self.sequence_so.get_next_char(self.sequence_so.number_next_actual)
        # An exception is forced by confirming a confirmed order
        with self.assertRaises(UserError):
            order.action_confirm()
        order.update({"state": "draft"})
        # Now the SQ can be confirmed
        order.action_confirm()
        # Checks that the faulty confirmation attempt did not consume a sequence number
        self.assertEqual(next_name, order.name)

    def test_copy_no_origin(self):
        order1 = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "company_id": self.company1.id,
            }
        )
        order_copy = order1.copy()
        # Check the duplicate has the original as origin
        self.assertEqual(order1.name, order_copy.origin)

    def test_copy_with_origin(self):
        origin = "origin"
        order1 = self.sale_order_model.create(
            {
                "origin": origin,
                "partner_id": self.partner.id,
                "company_id": self.company1.id,
            }
        )
        order_copy = order1.copy()
        # Check the duplicate has the original's origin prepended
        self.assertEqual(", ".join([origin, order1.name]), order_copy.origin)
