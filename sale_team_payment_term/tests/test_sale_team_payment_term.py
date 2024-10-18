# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleTeamPaymentTerm(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleTeamPaymentTerm, cls).setUpClass()
        cls.sale = cls.env.ref("sale.sale_order_1")

        cls.team = cls.env.ref("sales_team.team_sales_department")

        # res_partner_2 already have a payment term
        cls.partner = cls.env.ref("base.res_partner_2")

        cls.team_payment_term = cls.env.ref(
            "account.account_payment_term_end_following_month"
        )
        cls.sale_payment_term = cls.env.ref("account.account_payment_term_15days")
        cls.team.team_payment_term_id = cls.team_payment_term.id
        cls.sale.partner_id = cls.partner.id
        cls.sale.team_id = cls.team.id

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
        partner_2 = self.env.ref("base.res_partner_12")
        partner_2.property_payment_term_id = self.sale_payment_term
        self.sale.partner_id = partner_2.id
        self.assertEqual(self.sale.payment_term_id, partner_2.property_payment_term_id)

    def test_4_sale_payment_term(self):
        # sale payment term if exist
        self.sale.payment_term_id = self.sale_payment_term.id
        self.assertEqual(self.sale.payment_term_id, self.sale_payment_term)
