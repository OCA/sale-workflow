# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase

from .test_tax import TaxCase


class TaxPriceTaxState(TaxCase, SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sale = cls.env.ref("sale.sale_order_1")

        account_user_type = cls.env.ref("account.data_account_type_receivable")

        cls.account_rec = cls.env["account.account"].create(
            {
                "code": "TEST-REC",
                "name": "Rec - Test",
                "user_type_id": account_user_type.id,
                "reconcile": True,
            }
        )

        cls.account_sale = cls.env["account.account"].create(
            {
                "code": "TEST-SALE",
                "name": "Sale - Test",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_direct_costs"
                ).id,
            }
        )

        cls.sale_journal = cls.env["account.journal"].create(
            {
                "name": "Sale Journal - Test",
                "code": "SALE",
                "type": "sale",
                "default_account_id": cls.account_sale.id,
                "payment_debit_account_id": cls.account_sale.id,
                "payment_credit_account_id": cls.account_sale.id,
            }
        )

    def create_invoice(self, tax1, tax2):
        invoice = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "journal_id": self.sale_journal.id,
                    "invoice_line_ids": [
                        (
                            0,
                            None,
                            {
                                "product_id": self.product.id,
                                "quantity": 1,
                                "price_unit": 50,
                                "account_id": self.env["account.account"]
                                .search(
                                    [
                                        (
                                            "user_type_id",
                                            "=",
                                            self.env.ref(
                                                "account.data_account_type_revenue"
                                            ).id,
                                        )
                                    ],
                                    limit=1,
                                )
                                .id,
                                "tax_ids": [
                                    (
                                        6,
                                        0,
                                        tax1.ids,
                                    )
                                ],
                            },
                        ),
                        (
                            0,
                            None,
                            {
                                "product_id": self.product.id,
                                "quantity": 1,
                                "price_unit": 50,
                                "account_id": self.env["account.account"]
                                .search(
                                    [
                                        (
                                            "user_type_id",
                                            "=",
                                            self.env.ref(
                                                "account.data_account_type_revenue"
                                            ).id,
                                        )
                                    ],
                                    limit=1,
                                )
                                .id,
                                "tax_ids": [
                                    (
                                        6,
                                        0,
                                        tax2.ids,
                                    )
                                ],
                            },
                        ),
                    ],
                }
            ]
        )
        return invoice

    def test_sale_price_tax_include(self):
        self.sale.order_line.tax_id = self.tax_inc
        self.assertEqual(self.sale.price_tax_state, "include")

    def test_sale_price_tax_exclude(self):
        self.sale.order_line.tax_id = self.tax_exc
        self.assertEqual(self.sale.price_tax_state, "exclude")

    def test_sale_price_tax_exception(self):
        self.sale.order_line[0].tax_id = self.tax_inc
        self.sale.order_line[1].tax_id = self.tax_exc
        self.assertEqual(self.sale.price_tax_state, "exception")

    def test_invoice_price_tax_include(self):
        invoice = self.create_invoice(self.tax_inc, self.tax_inc)
        self.assertEqual(invoice.price_tax_state, "include")

    def test_invoice_price_tax_exclude(self):
        invoice = self.create_invoice(self.tax_exc, self.tax_exc)
        self.assertEqual(invoice.price_tax_state, "exclude")

    def test_invoice_price_tax_exception(self):
        invoice = self.create_invoice(self.tax_inc, self.tax_exc)
        self.assertEqual(invoice.price_tax_state, "exception")
