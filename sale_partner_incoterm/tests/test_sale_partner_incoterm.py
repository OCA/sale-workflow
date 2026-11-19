# Copyright 2015 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form, TransactionCase


class TestSalePartnerIncoterm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.address = cls.env["res.partner"].create({"name": "Incoterm Address"})
        cls.customer = cls.env["res.partner"].create(
            {"name": "Test Customer", "sale_incoterm_address_id": cls.address.id}
        )
        cls.customer_no_address = cls.env["res.partner"].create(
            {"name": "Customer Without Address"}
        )

    def test_incoterm_address_from_partner(self):
        with self.subTest(source="form"):
            sale_form = Form(self.env["sale.order"])
            sale_form.partner_id = self.customer
            self.assertEqual(sale_form.incoterm_address_id, self.address)
            sale_form.partner_id = self.customer_no_address
            self.assertFalse(sale_form.incoterm_address_id)
        with self.subTest(source="create"):
            orders = self.env["sale.order"].create(
                [
                    {"partner_id": self.customer.id},
                    {"partner_id": self.customer_no_address.id},
                ]
            )
            self.assertEqual(orders[0].incoterm_address_id, self.address)
            self.assertFalse(orders[1].incoterm_address_id)

    def test_incoterm_address_override(self):
        other_address = self.env["res.partner"].create({"name": "Other Address"})
        order = self.env["sale.order"].create(
            {"partner_id": self.customer.id, "incoterm_address_id": other_address.id}
        )
        self.assertEqual(order.incoterm_address_id, other_address)
