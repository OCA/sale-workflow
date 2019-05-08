# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestProductSupplierinfoForCustomerSale(TransactionCase):

    def setUp(self):
        super(TestProductSupplierinfoForCustomerSale, self).setUp()
        self.pricelist_model = self.env['product.pricelist']
        self.supplierinfo = self.env['product.supplierinfo']
        self.customer = self.env.ref('base.res_partner_1')
        self.product = self.env['product.product'].create(
            {'name': 'Name_product',
             'default_code': 'code_product'}
        ).with_context({'partner_id': self.customer.id,
                        'supplierinfo_type': 'customer'})
        self.supplierinforec = self.supplierinfo.create({
            'product_code': 'code_test',
            'product_name': 'Name_test',
            'name': self.customer.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'supplierinfo_type': 'customer',
            'price': 100.0,
            'min_qty': 15.0,
        })
        self.pricelist = self.env['product.pricelist'].create({
            'name': 'Test Pricelist',
            'currency_id': self.env.ref('base.USD').id,
        })
        self.company = self.env.ref('base.main_company')
        self.pricelist_item = self.env['product.pricelist.item'].create({
            'applied_on': '1_product',
            'base': 'list_price',
            'name': 'Test Pricelist Item',
            'pricelist_id': self.pricelist.id,
            'compute_price': 'fixed',
            'fixed_price': 100.0,
            'product_id': self.product.id,
        })

    def test_product_supplierinfo_for_customer_sale(self):
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'pricelist_id': self.pricelist.id,
        })
        line = self.env['sale.order.line'].create({
            'product_id': self.product.id,
            'order_id': so.id,
            'product_uom_qty': 15.0
        })
        line.product_id_change()
        self.assertEqual(
            line.product_customer_code, self.supplierinforec.product_code,
            "Error: Customer product code was not passed to sale order line")
        self.assertEqual(
            line.product_uom_qty, self.supplierinforec.min_qty,
            "Error: Min qty was not passed to the sale order line")
