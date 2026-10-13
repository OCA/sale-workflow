# Copyright 2015 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form, TransactionCase


class TestSalePartnerIncoterm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.incoterm = cls.env["account.incoterms"].search([], limit=1)
        cls.address = cls.env["res.partner"].create({"name": "Incoterm Address"})
        cls.customer.write(
            {
                "sale_incoterm_id": cls.incoterm.id,
                "sale_incoterm_address_id": cls.address.id,
            }
        )

    def test_sale_partner_incoterm(self):
        """
        Check that the customer's default incoterm is retrieved in the
        sales order's onchange
        """
        sale_order = Form(self.env["sale.order"])
        sale_order.partner_id = self.customer
        self.assertEqual(sale_order.incoterm, self.incoterm)
        self.assertEqual(sale_order.incoterm_address_id, self.address)

    def test_sale_partner_incoterm_create(self):
        """The customer's default incoterm is set on orders created by code"""
        sale_order = self.env["sale.order"].create({"partner_id": self.customer.id})
        self.assertEqual(sale_order.incoterm, self.incoterm)
        self.assertEqual(sale_order.incoterm_address_id, self.address)
