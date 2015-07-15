# -*- coding: utf-8 -*-
import unittest2


class test_product_bundle(unittest2.TestCase):
    """ Test Product bundle"""

    def setUp(self):
        super(test_product_bundle, self).setUp()

    def tearDown(self):
        super(test_product_bundle, self).tearDown()

    @classmethod
    def init(self):
        super(test_product_bundle, self).init()
        self.partner = self.env['res.partner']
        self.product = self.env['product.product']
        self.sale_order = self.env['sale.order']
        self.sale_order_line = self.env['sale.order.line']
        self.product_bundle = self.env['product.bundle']
        self.product_bundle_line = self.env['product.bundle.line']
        self.sale_order_bundle = self.env['sale.order.bundle']

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
        prod_2 = self.create_product('Product 2', 101, 151)
        prod_3 = self.create_product('Product 3', 102, 152)
        prod_4 = self.create_product('Product 4', 103, 153)
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
        self.create_sale_order_line(so, prod[1], 1)
        self.create_sale_order_line(so, prod[2], 1)
        self.create_sale_order_line(so, prod[3], 1)

        return so

    def create_product_bundle(self):
        return self.product_bundle.create({'name': 'Bundle test'})

    def create_product_bundle_line(self, bundle, product, quantity):
        return self.product_bundle_line.create({
            'product_bundle_id': bundle.id, 'product_id': product.id, 'quantity': quantity})

    def create_product_bundle_complete(self):
        bundle = self.create_product_bundle()
        prod = self._get_product()
        self.product_bundle_line.create({
            'product_bundle_id': bundle.id, 'product_id': prod[0], 'quantity': 2})

    def test_add_bundle(self):
        so = self.create_sale_order_complete()
        self._context.update(active_id=so.id)
        product_bundle_id = self.create_product_bundle_complete()
        so_bundle = self.sale_order_bundle.create({
            'product_bundle_id': product_bundle_id, 'quantity': 2})
        so_bundle.add_bundle()
