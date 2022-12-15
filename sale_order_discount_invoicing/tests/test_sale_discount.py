# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestSaleInvoiceDiscount(TransactionCase):

    # SETUP METHODS #

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpCompany()
        cls.setUpAccounts()
        cls.setUpTaxes()
        cls.setUpProducts()
        cls.setUpAccountJournal()
        cls.setUpSalePartner()

    @classmethod
    def setUpCompany(cls):
        """Set up main company"""
        cls.company = cls.env.ref("base.main_company")
        cls.company.country_id = cls.env.ref("base.fr")

    @classmethod
    def setUpAccounts(cls):
        """Set up accounts"""
        cls.account_tax = cls.env["account.account"].create(
            {
                "code": "VAT",
                "name": "VAT",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_current_assets"
                ).id,
                "company_id": cls.company.id,
            }
        )
        cls.account_income_product = cls.env["account.account"].create(
            {
                "code": "INCOME_PROD111",
                "name": "Income - Test Account",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_direct_costs"
                ).id,
                "company_id": cls.company.id,
            }
        )
        cls.account_discount_product = cls.env["account.account"].create(
            {
                "code": "DISCOUNT_PROD111",
                "name": "Discount - Test Account",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_direct_costs"
                ).id,
                "company_id": cls.company.id,
            }
        )
        cls.account_property_receivable = cls.env["account.account"].create(
            {
                "code": "X2020",
                "name": "Receivable - Test Account",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
                "company_id": cls.company.id,
            }
        )
        cls.account_income = cls.env["account.account"].create(
            {
                "code": "NC1112-1",
                "name": "Sale - Test Account",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_direct_costs"
                ).id,
                "company_id": cls.company.id,
            }
        )
        cls.account_revenue = cls.env["account.account"].create(
            {
                "code": "NC1114-1",
                "name": "Sales - Test Sales Account",
                "user_type_id": cls.env.ref("account.data_account_type_revenue").id,
                "reconcile": True,
                "company_id": cls.company.id,
            }
        )

    @classmethod
    def setUpTaxes(cls):
        """Set up some taxes"""
        cls.tax_price_include = cls.env["account.tax"].create(
            {
                "name": "10.0% incl",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 10.0,
                "price_include": True,
                "include_base_amount": False,
                "country_id": cls.env.ref("base.fr").id,
                "invoice_repartition_line_ids": [
                    (
                        0,
                        0,
                        {"factor_percent": 100, "repartition_type": "base"},
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.account_tax.id,
                        },
                    ),
                ],
                "refund_repartition_line_ids": [
                    (
                        0,
                        0,
                        {"factor_percent": 100, "repartition_type": "base"},
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.account_tax.id,
                        },
                    ),
                ],
            }
        )
        cls.tax_price_exclude = cls.env["account.tax"].create(
            {
                "name": "10.0% excl",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 10.0,
                "price_include": False,
                "include_base_amount": False,
                "country_id": cls.env.ref("base.fr").id,
                "invoice_repartition_line_ids": [
                    (
                        0,
                        0,
                        {"factor_percent": 100, "repartition_type": "base"},
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.account_tax.id,
                        },
                    ),
                ],
                "refund_repartition_line_ids": [
                    (
                        0,
                        0,
                        {"factor_percent": 100, "repartition_type": "base"},
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.account_tax.id,
                        },
                    ),
                ],
            }
        )

    @classmethod
    def setUpProducts(cls):
        """Set up some additional products, categories, etc..."""
        cls.product_discount_category = cls.env["product.category"].create(
            {
                "name": "Product Category with Discount account",
                "property_account_income_categ_id": cls.account_income_product.id,
                "property_account_discount_categ_id": cls.account_discount_product.id,
            }
        )
        cls.product_order_tax_excluded = cls.env["product.product"].create(
            {
                "name": "Product Test Excluded",
                "standard_price": 100,
                "list_price": 100,
                "type": "consu",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "order",
                "expense_policy": "no",
                "default_code": "PROD_ORDER_Excluded",
                "taxes_id": [(6, 0, [cls.tax_price_exclude.id])],
                "categ_id": cls.product_discount_category.id,
            }
        )
        cls.product_order_tax_included = cls.env["product.product"].create(
            {
                "name": "Product Test 1 Included",
                "standard_price": 100,
                "list_price": 100,
                "type": "consu",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "order",
                "expense_policy": "no",
                "default_code": "PROD_ORDER_Included",
                "taxes_id": [(6, 0, [cls.tax_price_include.id])],
                "categ_id": cls.product_discount_category.id,
            }
        )

    @classmethod
    def setUpAccountJournal(cls):
        """Set up some additional journals"""
        cls.journal_sale_company = cls.env["account.journal"].create(
            {
                "name": "Sale Journal - Test",
                "code": "AJ-SALE",
                "type": "sale",
                "company_id": cls.company.id,
                "default_account_id": cls.account_income.id,
            }
        )

    @classmethod
    def setUpSalePartner(cls):
        """Set up sale order's partner"""
        cls.partner1 = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "company_id": False,
                "property_account_receivable_id": cls.account_property_receivable.id,
                "country_id": cls.env.ref("base.fr").id,
            }
        )

    # COMMON TOOLS #

    def _run_test(self, tax_type: str, company_param: bool, with_discount: bool):
        self._set_company_param(company_param)
        self._create_so(tax_type=tax_type, with_discount=with_discount)
        self._confirm_so()
        self._create_invoice()
        self._test_results(company_param=company_param, with_discount=with_discount)

    def _set_company_param(self, company_param: bool):
        self.company.account_split_discount_line = company_param

    def _create_so(self, tax_type: str, with_discount: bool):
        if tax_type == "excluded":
            product = self.product_order_tax_excluded
            origin_price_unit = 1250
            price_unit = 1000 if with_discount else origin_price_unit
        elif tax_type == "included":
            product = self.product_order_tax_included
            origin_price_unit = 1375
            price_unit = 1100 if with_discount else origin_price_unit
        else:
            raise ValueError
        self.current_sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "partner_invoice_id": self.partner1.id,
                "partner_shipping_id": self.partner1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "price_unit": price_unit,
                            "origin_price_unit": origin_price_unit,
                        },
                    )
                ],
            }
        )

    def _confirm_so(self):
        assert self.current_sale_order
        self.current_sale_order.action_confirm()

    def _create_invoice(self):
        assert self.current_sale_order
        old_invoices = self.current_sale_order.invoice_ids
        wiz = (
            self.env["sale.advance.payment.inv"]
            .with_context(
                **{
                    "active_model": "sale.order",
                    "active_ids": [self.current_sale_order.id],
                    "active_id": self.current_sale_order.id,
                    "default_journal_id": self.journal_sale_company.id,
                }
            )
            .create({"advance_payment_method": "delivered"})
        )
        wiz.create_invoices()
        self.current_invoice = self.current_sale_order.invoice_ids - old_invoices

    def _test_results(self, company_param: bool, with_discount: bool):
        created = [
            (
                line.account_id.id,
                line.debit,
                line.credit,
                line.discount_split_by_sale_line_id.id,
                line.is_split_line,
                line.is_split_discount_line,
            )
            for line in self.current_invoice.line_ids.sorted(
                lambda l: (l.debit, l.credit)
            )
        ]
        if with_discount:
            if company_param:
                expected = [
                    (self.account_tax.id, 0.0, 100.0, False, False, False),
                    (
                        self.account_income_product.id,
                        0.0,
                        1250.0,
                        self.current_sale_order.order_line.id,
                        True,
                        False,
                    ),
                    (
                        self.account_discount_product.id,
                        250.0,
                        0.0,
                        self.current_sale_order.order_line.id,
                        True,
                        True,
                    ),
                    (
                        self.account_property_receivable.id,
                        1100.0,
                        0.0,
                        False,
                        False,
                        False,
                    ),
                ]
            else:
                expected = [
                    (self.account_tax.id, 0.0, 100.0, False, False, False),
                    (self.account_income_product.id, 0.0, 1000.0, False, False, False),
                    (
                        self.account_property_receivable.id,
                        1100.0,
                        0.0,
                        False,
                        False,
                        False,
                    ),
                ]
        else:
            expected = [
                (self.account_tax.id, 0.0, 125.0, False, False, False),
                (self.account_income_product.id, 0.0, 1250.0, False, False, False),
                (self.account_property_receivable.id, 1375.0, 0.0, False, False, False),
            ]
        self.assertEqual(created, expected)
        for line in self.current_sale_order.order_line:
            self.assertEqual(line.qty_invoiced, line.product_uom_qty)

    # PROPER TESTS #

    def test_00_invoicing_discount_tax_excluded(self):
        self._run_test(tax_type="excluded", company_param=True, with_discount=True)

    def test_01_invoicing_discount_tax_included(self):
        self._run_test(tax_type="included", company_param=True, with_discount=True)

    def test_02_invoicing_no_discount_tax_excluded(self):
        self._run_test(tax_type="excluded", company_param=True, with_discount=False)

    def test_03_invoicing_no_discount_tax_included(self):
        self._run_test(tax_type="included", company_param=True, with_discount=False)

    def test_04_invoicing_discount_tax_excluded_no_splitting_by_config(self):
        self._run_test(tax_type="excluded", company_param=False, with_discount=True)

    def test_05_invoicing_discount_tax_included_no_splitting_by_config(self):
        self._run_test(tax_type="included", company_param=False, with_discount=True)

    def test_06_invoicing_no_discount_tax_excluded_no_splitting_by_config(self):
        self._run_test(tax_type="excluded", company_param=False, with_discount=False)

    def test_07_invoicing_no_discount_tax_included_no_splitting_by_config(self):
        self._run_test(tax_type="included", company_param=False, with_discount=False)

    def test_08_raise_update_error_from_form_view(self):
        self._set_company_param(True)
        self._create_so(tax_type="excluded", with_discount=True)
        self._confirm_so()
        self._create_invoice()
        with self.assertRaisesRegex(
            ValidationError, "Please create/delete/modify both lines."
        ):
            with Form(self.current_invoice) as invoice_form:
                with invoice_form.invoice_line_ids.edit(0) as invoice_line:
                    invoice_line.quantity += 1

    def test_09_raise_delete_error_from_form_view(self):
        self._set_company_param(True)
        self._create_so(tax_type="excluded", with_discount=True)
        self._confirm_so()
        self._create_invoice()
        with self.assertRaisesRegex(
            ValidationError, "Please create/delete/modify both lines."
        ):
            with Form(self.current_invoice) as invoice_form:
                invoice_form.invoice_line_ids.remove(0)
