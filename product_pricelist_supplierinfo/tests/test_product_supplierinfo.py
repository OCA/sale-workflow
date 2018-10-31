# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common


class TestProductSupplierinfo(common.SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestProductSupplierinfo, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner Test',
        })
        cls.supplier1 = cls.env['res.partner'].create({
            'name': 'Supplier #1',
        })
        cls.supplier2 = cls.env['res.partner'].create({
            'name': 'Supplier #2',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product Test',
            'seller_ids': [
                (0, 0, {
                    'name': cls.supplier1.id,
                    'min_qty': 5,
                    'price': 50,
                }),
                (0, 0, {
                    'name': cls.supplier2.id,
                    'min_qty': 1,
                    'price': 10,
                }),
            ],
        })
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'Supplierinfo Pricelist',
            'discount_policy': 'without_discount',
            'item_ids': [
                (0, 0, {
                    'compute_price': 'formula',
                    'base': 'supplierinfo',
                    'price_discount': 0,
                    'min_quantity': 1.0,
                }),
            ],
        })

    def test_pricelist_based_on_product_category(self):
        self.pricelist.item_ids[0].write({
            'price_discount': 50,
            'applied_on': '2_product_category',
            'categ_id': self.env.ref('product.product_category_all').id,
        })
        self.assertAlmostEqual(
            self.pricelist.get_product_price(self.product, 1, False), 5.0,
        )

    def test_pricelist_based_on_product(self):
        self.pricelist.item_ids[0].write({
            'applied_on': '1_product',
            'product_tmpl_id': self.product.product_tmpl_id.id,
        })
        self.assertAlmostEqual(
            self.pricelist.get_product_price(self.product, 1, False), 10.0,
        )

    def test_pricelist_based_on_product_variant(self):
        self.pricelist.item_ids[0].write({
            'price_discount': -25,
            'applied_on': '0_product_variant',
            'product_id': self.product.id,
        })
        self.assertAlmostEqual(
            self.pricelist.get_product_price(self.product, 1, False), 12.5,
        )

    def test_pricelist_min_quantity(self):
        self.assertAlmostEqual(
            self.pricelist.get_product_price(self.product, 1, False), 10,
        )
        self.assertAlmostEqual(
            self.pricelist.get_product_price(self.product, 5, False), 50,
        )
        self.pricelist.item_ids[0].no_supplierinfo_min_quantity = True
        self.assertAlmostEqual(
            self.pricelist.get_product_price(self.product, 5, False), 10,
        )

    def test_pricelist_dates(self):
        """ Test pricelist and supplierinfo dates """
        self.product.seller_ids.filtered(
            lambda x: x.min_qty == 5
        ).date_start = '2018-12-31'
        self.assertAlmostEqual(
            self.pricelist.get_product_price(
                self.product, 5, False, date='2018-10-01',
            ), 0,
        )
        self.assertAlmostEqual(
            self.pricelist.get_product_price(
                self.product, 5, False, date='2019-01-01',
            ), 50,
        )
