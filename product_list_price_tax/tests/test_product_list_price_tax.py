# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestProductListPriceTax(common.SavepointCase):

    @classmethod
    def setUpClass(self):
        super(TestProductListPriceTax, self).setUpClass()
        self.ProductTemplate = self.env['product.template']
        self.tax_group = self.env['account.tax.group'].create({
            'name': 'Tax group test'
        })
        self.AccountTax = self.env['account.tax']
        self.account_tax = self.AccountTax.create({
            'name': 'Sale-Test-21%',
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group.id,
            'amount': 21.00,
        })
        self.product_template = self.ProductTemplate.create({
            'name': 'Product - template - Test',
            'taxes_id': [(6, 0, self.account_tax.ids)],
            'list_price': 1000.00,
            'list_price_tax': 1210.00,
        })

    def test_create_product_tax(self):
        product_template_tax = self.ProductTemplate.create({
            'name': 'Product - template - Test',
            'taxes_id': [(6, 0, self.account_tax.ids)],
            'list_price_tax': 1210.00,
        })
        self.assertEquals(product_template_tax.list_price, 1000.00)

    def test_create_product_without_tax(self):
        product_template_tax = self.ProductTemplate.create({
            'name': 'Product - template - Test',
            'taxes_id': [(6, 0, self.account_tax.ids)],
            'list_price': 1000.00,
        })
        self.assertEquals(product_template_tax.list_price_tax, 1210.00)

    def test_write_product_tax(self):
        self.product_template.list_price_tax = 2240.00
        self.assertEquals(self.product_template.list_price, 1851.24)
        self.product_template.list_price = 1000.00
        self.assertEquals(self.product_template.list_price_tax, 1210.00)
