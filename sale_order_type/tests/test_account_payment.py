from odoo.tests.common import TransactionCase


class TestAccountPayment(TransactionCase):
    def setUp(self):
        super().setUp()
        self.AccountPayment = self.env["account.payment"]
        self.Journal = self.env["account.journal"]

        self.env["res.currency"].search(
            [("active", "=", False), ("name", "=", "EUR")]
        ).write({"active": True})

        self.company_currency = self.env.company.currency_id
        self.currency_eur = self.env["res.currency"].search([("name", "=", "EUR")])

        self.journal_usd = self.Journal.create(
            {
                "name": "USD Journal",
                "type": "bank",
                "currency_id": self.company_currency.id,
            }
        )

        self.journal_eur = self.Journal.create(
            {"name": "EUR Journal", "type": "bank", "currency_id": self.currency_eur.id}
        )

        self.payment = self.AccountPayment.create(
            {
                "journal_id": self.journal_usd.id,
                "payment_type": "inbound",
                "amount": 10.0,
                "currency_id": self.company_currency.id,
            }
        )

    def test_compute_currency_id(self):
        # Test the scenario when currency is the same as company's currency
        self.assertEqual(self.payment.currency_id, self.company_currency)

        # Test that currency is computed correctly when it differs
        # from the company's currency
        self.payment.write({"currency_id": self.currency_eur.id})
        self.payment._compute_currency_id()
        self.assertEqual(self.payment.currency_id, self.currency_eur)

        # Test that currency remains the same if it differs from the journal's currency
        self.payment.journal_id = self.journal_eur
        self.payment._compute_currency_id()
        self.assertEqual(self.payment.currency_id, self.currency_eur)

        # Scenario to replicate the error condition: journal company currency different
        # from payment currency
        self.payment._compute_currency_id()
        self.assertNotEqual(
            self.payment.currency_id, self.payment.journal_id.company_id.currency_id
        )
