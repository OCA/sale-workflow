# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestMultiCompany(TransactionCase):

    def create_company(self, values):
        company = self.env['res.company'].create(values)
        return company

    def create_product(self, values):
        values.update({
            'type': 'consu',
            'invoice_policy': 'order',
        })
        product_template = self.env['product.template'].create(values)
        return product_template.product_variant_id

    def setUp(self):
        super(TestMultiCompany, self).setUp()
        coa = self.env.user.company_id.chart_template_id
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

        self.company_be = self.create_company({
            'name': 'Belgian company',
            'currency_id': self.env.ref('base.EUR').id,
            'country_id': self.env.ref('base.be').id
        })

        self.company_fr_daughter = self.create_company({
            'name': 'French company daughter',
            'currency_id': self.env.ref('base.EUR').id,
            'country_id': self.env.ref('base.fr').id
        })

        self.env.user.company_ids |= self.company_ch
        self.env.user.company_ids |= self.company_fr
        self.env.user.company_ids |= self.company_be
        self.env.user.company_ids |= self.company_fr_daughter

        self.env.user.company_id = self.company_fr.id
        coa.try_loading_for_current_company()
        self.customer_fr = self.env['res.partner'].create(
            {
                'name': 'Customer FR',
            }
        )

        self.product_fr = self.create_product({
            'name': 'Evian bottle',
            'list_price': 2.0,
        })

        self.env.user.company_id = self.company_ch.id
        coa.try_loading_for_current_company()
        self.customer_ch = self.env['res.partner'].create(
            {
                'name': 'Customer CH',
            }
        )

        self.product_ch = self.create_product({
            'name': 'Henniez bottle',
            'list_price': 3.0,
        })

        self.env.user.company_id = self.company_be.id
        coa.try_loading_for_current_company()

        self.customer_be = self.env['res.partner'].create(
            {
                'name': 'Customer BE',
            }
        )

        self.product_be = self.env['product.template'].create({
            'name': 'SPA bottle',
            'list_price': 1.5,
            'type': 'consu',
            'invoice_policy': 'order',
        }).product_variant_id

        self.env.user.company_id = self.company_fr_daughter.id
        coa.try_loading_for_current_company()
        self.customer_fr_daughter = self.env['res.partner'].create(
            {
                'name': 'Customer FR Daughter',
            }
        )
        self.product_fr_daughter = self.create_product({
            'name': 'Contrex bottle',
            'list_price': 1.5,
        })

        self.auto_wkf = self.env.ref(
            'sale_automatic_workflow.automatic_validation'
        )
        self.env.user.company_id = self.env.ref('base.main_company')

    def create_auto_wkf_order(self, company, customer, product, qty):
        SaleOrder = self.env['sale.order']

        self.product_uom_unit = self.env.ref('uom.product_uom_unit')

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
        order_be = self.create_auto_wkf_order(self.company_be,
                                              self.customer_be,
                                              self.product_be, 10)

        order_fr_daughter = self.create_auto_wkf_order(
            self.company_fr_daughter, self.customer_fr_daughter,
            self.product_fr_daughter, 4)

        self.assertEquals(order_fr.state, 'draft')
        self.assertEquals(order_ch.state, 'draft')
        self.assertEquals(order_be.state, 'draft')
        self.assertEquals(order_fr_daughter.state, 'draft')

        self.env['automatic.workflow.job'].run()
        invoice_fr = order_fr.invoice_ids
        invoice_ch = order_ch.invoice_ids
        invoice_be = order_be.invoice_ids
        invoice_fr_daughter = order_fr_daughter.invoice_ids
        self.assertEquals(invoice_fr.state, 'open')
        self.assertEquals(invoice_fr.journal_id.company_id,
                          order_fr.company_id)
        self.assertEquals(invoice_ch.state, 'open')
        self.assertEquals(invoice_ch.journal_id.company_id,
                          order_ch.company_id)
        self.assertEquals(invoice_be.state, 'open')
        self.assertEquals(invoice_be.journal_id.company_id,
                          order_be.company_id)
        self.assertEquals(invoice_fr_daughter.state, 'open')
        self.assertEquals(invoice_fr_daughter.journal_id.company_id,
                          order_fr_daughter.company_id)
