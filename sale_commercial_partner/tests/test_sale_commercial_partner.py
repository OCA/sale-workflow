# Copyright (C) 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, common


class TestSaleCommercialPartner(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.commercial_partner = self.env["res.partner"].create(
            {
                "is_company": False,
                "name": "Commercial Partner",
            }
        )

        self.partner = self.env["res.partner"].create(
            {
                "is_company": False,
                "name": "Partner",
                "parent_id": self.commercial_partner.id,
            }
        )

    def test_01_default_commercial_partner_on_sale_order(self):
        """
        Test defaulting commercial partner on sale order
        :return:
        """

        with Form(self.env["sale.order"]) as order_form:
            order_form.partner_id = self.partner
        order_01 = order_form.save()

        self.assertEqual(order_01.partner_id, self.partner)
        self.assertEqual(order_01.commercial_partner_id, self.commercial_partner)
