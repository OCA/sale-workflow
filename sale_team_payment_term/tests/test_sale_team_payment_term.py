# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestSaleTeamPaymentTerm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.team_payment_term = cls.env["account.payment.term"].create(
            {"name": "Team Payment Term"}
        )
        cls.sale_payment_term = cls.env["account.payment.term"].create(
            {"name": "Sale Payment Term"}
        )
        cls.partner_payment_term = cls.env["account.payment.term"].create(
            {"name": "Partner Payment Term"}
        )

        cls.team = cls.env["crm.team"].create(
            {
                "name": "Test Sales Team",
                "team_payment_term_id": cls.team_payment_term.id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "property_payment_term_id": cls.partner_payment_term.id,
            }
        )

        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "team_id": cls.team.id,
            }
        )

    def test_1_team_payment_term(self):
        # sale team payment term if not in both partner and sale
        self.partner.property_payment_term_id = False
        self.assertEqual(self.sale.payment_term_id, self.team_payment_term)

    def test_2_partner_payment_term(self):
        # partner payment term if not in sale
        self.assertEqual(
            self.sale.payment_term_id, self.partner.property_payment_term_id
        )

    def test_3_onchange_partner(self):
        # change partner
        partner_2 = self.env["res.partner"].create(
            {
                "name": "Partner 2",
                "property_payment_term_id": self.sale_payment_term.id,
            }
        )
        self.sale.partner_id = partner_2.id
        self.assertEqual(self.sale.payment_term_id, partner_2.property_payment_term_id)

    def test_4_sale_payment_term(self):
        # sale payment term if exist
        self.sale.payment_term_id = self.sale_payment_term.id
        self.assertEqual(self.sale.payment_term_id, self.sale_payment_term)
