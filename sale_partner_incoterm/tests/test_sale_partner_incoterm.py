# Copyright 2015 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSalePartnerIncoterm(TransactionCase):
    def test_sale_partner_incoterm(self):
        """
        Check that the customer's default incoterm is retrieved in the
        sales order's onchange
        """
        customer = self.env.ref("base.res_partner_3")
        incoterm = self.env["account.incoterms"].search([], limit=1)
        customer.write({"sale_incoterm_id": incoterm.id})
        sale_order = self.env["sale.order"].create({"partner_id": customer.id})
        sale_order.onchange_partner_id()
        self.assertEqual(sale_order.incoterm, incoterm)
