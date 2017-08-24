# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMultiCompany(TransactionCase):

    def create_company(self, values):
        company = self.env['res.company'].create(values)
        return company

    def configure_basic_accounting(self, company_id):
        Account = self.env['account.account']
        income = Account.create({
            'name': 'Income',
            'code': 'INC',
            'user_type_id':
                self.env.ref('account.data_account_type_revenue').id,
            'company_id': company_id
        })
        receivable = Account.create({
            'name': 'Receivable',
            'code': 'REC',
            'user_type_id':
                self.env.ref('account.data_account_type_receivable').id,
            'reconcile': True,
            'company_id': company_id
        })
        payable = Account.create({
            'name': 'Payable',
            'code': 'PAY',
            'user_type_id':
                self.env.ref('account.data_account_type_payable').id,
            'reconcile': True,
            'company_id': company_id
        })
        Journal = self.env['account.journal']
        sale_journal = Journal.create({
            'name': 'Customer Invoices',
            'type': 'sale',
            'code': 'INV',
            'company_id': company_id,
            'default_debit_account_id': income.id,
            'default_credit_account_id': income.id,
        })
        return {'company_id': company_id,
                'income': income,
                'payable': payable,
                'receivable': receivable,
                'sale_journal': sale_journal}

    def create_partner(self, name, accounting_dict):
        return self.env['res.partner'].create({
            'name': name,
            'property_account_receivable_id': accounting_dict['receivable'].id,
            'property_account_payable_id': accounting_dict['payable'].id
        })

    def create_product(self, values):
        values.update({
            'type': 'consu',
            'invoice_policy': 'order',
        })
        product_template = self.env['product.template'].create(values)
        return product_template.product_variant_id

    def setUp(self):
        super(TestMultiCompany, self).setUp()

        self.company_fr = self.create_company({
            'name': 'French company',
            'currency_id': self.env.ref('base.EUR').id,
            'country_id': self.env.ref('base.fr').id
        })

        self.company_ch = self.create_company({
            'name': 'Swiss company',
            'currency_id': self.env.ref('base.CHF').id,
            'country_id': self.env.ref('base.ch').id
        })

        self.company_fr_daughter = self.create_company({
            'name': 'French company daughter',
            'currency_id': self.env.ref('base.EUR').id,
            'country_id': self.env.ref('base.fr').id
        })

        self.env.user.company_ids |= self.company_ch
        self.env.user.company_ids |= self.company_fr

        self.env.user.company_id = self.company_fr.id
        accounting_fr = self.configure_basic_accounting(self.company_fr.id)
        self.customer_fr = self.create_partner('Customer FR', accounting_fr)

        self.product_fr = self.create_product({
            'name': 'Evian bottle',
            'list_price': 2.0,
            'property_account_income_id': accounting_fr['income']
        })

        self.env.user.company_id = self.company_ch.id
        accounting_ch = self.configure_basic_accounting(self.company_ch.id)
        self.customer_ch = self.create_partner('Customer CH', accounting_ch)

        self.product_ch = self.create_product({
            'name': 'Henniez bottle',
            'list_price': 3.0,
            'property_account_income_id': accounting_ch['income']
        })

        self.env.user.company_id = self.company_fr_daughter.id
        accounting_fr_daughter = self.configure_basic_accounting(
            self.company_fr_daughter.id)
        self.customer_fr_daughter = self.create_partner('Customer FR Daughter',
                                                        accounting_fr_daughter)

        self.product_fr_daughter = self.create_product({
            'name': 'Contrex bottle',
            'list_price': 1.5,
            'property_account_income_id': accounting_fr_daughter['income']
        })

        self.auto_wkf = self.env.ref(
            'sale_automatic_workflow.automatic_validation')
        self.env.user.company_id = self.env.ref('base.main_company')

    def create_auto_wkf_order(self, company, customer, product, qty):
        SaleOrder = self.env['sale.order']

        self.product_uom_unit = self.env.ref('product.product_uom_unit')

        order = SaleOrder.create({
            'partner_id': customer.id,
            'company_id': company.id,
            'workflow_process_id': self.auto_wkf.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'price_unit': product.list_price,
                'product_uom_qty': qty,
                'product_uom': self.product_uom_unit.id,
            })]
        })
        return order

    def test_sale_order_multicompany(self):

        self.env.user.company_id = self.env.ref('base.main_company')
        order_fr = self.create_auto_wkf_order(self.company_fr,
                                              self.customer_fr,
                                              self.product_fr, 5)
        order_ch = self.create_auto_wkf_order(self.company_ch,
                                              self.customer_ch,
                                              self.product_ch, 10)
        order_fr_daughter = self.create_auto_wkf_order(
            self.company_fr_daughter, self.customer_fr_daughter,
            self.product_fr_daughter, 4)

        self.assertEquals(order_fr.state, 'draft')
        self.assertEquals(order_ch.state, 'draft')
        self.assertEquals(order_fr_daughter.state, 'draft')

        self.env['automatic.workflow.job'].run()
        invoice_fr = order_fr.invoice_ids
        invoice_ch = order_ch.invoice_ids
        invoice_fr_daughter = order_fr_daughter.invoice_ids
        self.assertEquals(invoice_fr.state, 'open')
        self.assertEquals(invoice_ch.state, 'open')
        self.assertEquals(invoice_fr_daughter.state, 'open')
