# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) info@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp.tests import TransactionCase


class TestProductNameSearch(TransactionCase):
    """Test for:
        - Assign a configuration customer for product.
        - Test product name_search
    """
    def setUp(self):
        super(TestProductNameSearch, self).setUp()
        self.customer = self.env.ref('base.res_partner_9')
        self.customer_1 = self.env.ref('base.res_partner_2')
        self.product = self.env['product.product'].create(
            {'name': 'Name_product',
             'default_code': 'code_product', }).with_context(
                 {'partner_id': self.customer.id,
                  'supplierinfo_type': 'customer'})
        self.supplierinfo = self.env['product.supplierinfo']

        self.supplierinfo_dict = {
            'product_code': 'code_test',
            'product_name': 'Name_test',
            'name': self.customer.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'type': 'customer',
        }

    def test_10_find_product_customer_code(self):
        """Assign a product_supplierinfo to the product and then search it
        using name_search
        """
        self.assertFalse(self.product.customer_ids)

        self.supplierinfo.create(self.supplierinfo_dict)
        self.assertTrue(self.product.customer_ids)

        # Search by product customer code
        product_names = self.product.name_search(name='code_test')
        self.assertEquals(len(product_names), 1)
        self.assertEquals(self.product.id, product_names[0][0])
        self.assertEquals('[code_test] Name_test', product_names[0][1])

        # Search by product default code with the customer used in
        # configuration customer
        product_names = self.product.name_search(name='code_product')
        self.assertEquals(len(product_names), 1)
        self.assertEquals(self.product.id, product_names[0][0])
        self.assertEquals('[code_test] Name_test', product_names[0][1])

        # Search by product default code with a different customer used in
        # configuration customer
        product_names = self.product.with_context(
            partner_id=self.customer_1.id).name_search(name='code_product')
        self.assertEquals(len(product_names), 1)
        self.assertEquals(self.product.id, product_names[0][0])
        self.assertEquals('[code_product] Name_product', product_names[0][1])

        # Create a product_1 with default_code similar to customer_code of
        # product, then name_search must find two products
        self.product_1 = self.env['product.product'].create(
            {'name': 'Name_test_1',
             'default_code': 'code_test_1', }).with_context(
                 {'partner_id': self.customer.id,
                  'supplierinfo_type': 'customer'})

        self.assertFalse(self.product_1.customer_ids)

        # Search by product customer code
        product_names = self.product.name_search(name='code_test')
        self.assertEquals(len(product_names), 2)
        product_names = product_names[0] + product_names[1]
        self.assertIn(self.product.id, product_names)
        self.assertIn(self.product_1.id, product_names)
        self.assertIn('[code_test] Name_test', product_names)
        self.assertIn('[code_test_1] Name_test_1', product_names)
