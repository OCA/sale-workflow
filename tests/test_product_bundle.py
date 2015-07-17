# -*- coding: utf-8 -*-
from openerp.tests import common


class test_product_bundle(common.TransactionCase):
    """ Test Product bundle"""

    def setUp(self):
        super(test_product_bundle, self).setUp()
        self.partner = self.env['res.partner']
        self.product = self.env['product.product']
        self.sale_order = self.env['sale.order']
        self.sale_order_line = self.env['sale.order.line']
        self.product_bundle = self.env['product.bundle']
        self.product_bundle_line = self.env['product.bundle.line']
        self.sale_order_bundle = self.env['sale.order.bundle']

    def tearDown(self):
        super(test_product_bundle, self).tearDown()

    def create_partner(self):
        return self.partner.create({
            'name': 'Clovis Nzouendjou', 'website': 'http://anybox.fr',
            'email': 'clovis@anybox.fr'
        })

    def create_product(self, name, standard_price, list_price):
        return self.product.create({
            'name': name,
            'sale_ok': True,
            'type': 'consu',
            'standard_price': standard_price,
            'list_price': list_price,
        })

    def _get_product(self):
        prod_1 = self.create_product('Product 1', 100, 150)
        prod_2 = self.create_product('Product 2', 200, 250)
        prod_3 = self.create_product('Product 3', 300, 350)
        prod_4 = self.create_product('Product 4', 400, 450)
        return [prod_1, prod_2, prod_3, prod_4]

    def create_sale_order(self):
        return self.sale_order.create({
            'partner_id': self.create_partner().id,
        })

    def create_sale_order_line(self, so, product, quantity):
        sol_data = {
            'order_id': so.id,
            'description': product.name,
            'product_id': product.id,
            'price_unit': product.list_price,
            'product_uom_qty': quantity,
        }
        return self.sale_order_line.create(sol_data)

    def create_sale_order_complete(self):
        so = self.create_sale_order()
        prod = self._get_product()

        self.create_sale_order_line(so, prod[0], 1)
        self.create_sale_order_line(so, prod[1], 2)

        return so

    def create_product_bundle(self):
        return self.product_bundle.create({'name': 'Bundle test'})

    def create_product_bundle_line(self, bundle, product, quantity):
        return self.product_bundle_line.create({
            'product_bundle_id': bundle.id, 'product_id': product.id, 'quantity': quantity})

    def create_product_bundle_complete(self):
        bundle = self.create_product_bundle()
        products = self._get_product()
        for product in products:
            self.product_bundle_line.create({
                'product_bundle_id': bundle.id, 'product_id': product.id, 'quantity': 2})
        return bundle

    def test_add_bundle(self):
        # Create a sale.order with 02 lines
        so = self.create_sale_order_complete()
        self.assertEquals(len(so.order_line), 2)
        # Checking sale order price
        self.assertEquals(so.amount_untaxed, 650)  # (150*1)+(250*2)
        self.assertEquals(so.amount_tax, 0)  # without tax
        self.assertEquals(so.amount_total, 650)

        # Create a bundle which contains 04 products
        product_bundle = self.create_product_bundle_complete()
        # Simulation the opening of the wizard and adding a bundle on the current sale order
        so_bundle = self.sale_order_bundle.with_context(active_id=so.id).create({
            'product_bundle_id': product_bundle.id, 'quantity': 1})
        so_bundle.add_bundle()
        # checking our sale order
        self.assertEquals(len(so.order_line), 6)
        # (150*1)+(250*2)+(150*2)+(250*2)+(350*2)+(450*2) =
        self.assertEquals(so.amount_untaxed, 3050)
        self.assertEquals(so.amount_tax, 0)  # without tax
        self.assertEquals(so.amount_total, 3050)
