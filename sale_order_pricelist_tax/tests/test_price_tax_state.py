# © 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import Form
from odoo.tests.common import TransactionCase

from .test_tax import TaxCase


class TaxPriceTaxState(TaxCase, TransactionCase):
    allow_inherited_tests_method = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        order_form = Form(cls.env["sale.order"].with_context(tracking_disable=True))
        order_form.partner_id = cls.env.ref("base.res_partner_10")
        with order_form.order_line.new() as line:
            line.product_id = cls.product
            line.product_uom_qty = 1.0
        with order_form.order_line.new() as line:
            line.product_id = cls.product
            line.product_uom_qty = 1.0
        cls.sale = order_form.save()
        cls.account_rec = cls.env["account.account"].create(
            {
                "code": "TESTREC",
                "name": "Rec - Test",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.account_sale = cls.env["account.account"].create(
            {
                "code": "TESTSALE",
                "name": "Sale - Test",
                "account_type": "expense_direct_cost",
            }
        )
        cls.sale_journal = cls.env["account.journal"].create(
            {
                "name": "Sale Journal - Test",
                "code": "SALE",
                "type": "sale",
                "default_account_id": cls.account_sale.id,
            }
        )

    def create_invoice(self, tax1, tax2):
        account_income = self.env["account.account"].search(
            [("account_type", "=", "income")], limit=1
        )

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
                                "account_id": account_income.id,
                                "tax_ids": [(6, 0, tax1.ids)],
                            },
                        ),
                        (
                            0,
                            None,
                            {
                                "product_id": self.product.id,
                                "quantity": 1,
                                "price_unit": 50,
                                "account_id": account_income.id,
                                "tax_ids": [(6, 0, tax2.ids)],
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
