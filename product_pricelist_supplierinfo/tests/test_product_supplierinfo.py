# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common


class TestProductSupplierinfo(common.SavepointCase):
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
        cls.public_pricelist = cls.env.ref('product.list0')
        cls.supplierinfo_pricelist = cls.env['product.pricelist'].create({
            'name': 'Supplierindo Pricelist',
            'discount_policy': 'without_discount',
        })

    def create_sale(self):
        return self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'date_order': '2018-12-31',
            'pricelist_id': self.supplierinfo_pricelist.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
            })],
        })

    def test_pricelist_based_on_product_category(self):
        sale_orden = self.create_sale()
        order_line = sale_orden.order_line[0]
        self.supplierinfo_pricelist.item_ids = [(0, 0, {
            'compute_price': 'formula',
            'base': 'supplierinfo',
            'price_discount': 50,
            'min_quantity': 1.0,
            'applied_on': '2_product_category',
            'categ_id': self.env.ref('product.product_category_all').id,
        })]
        order_line.product_id_change()
        self.assertAlmostEqual(order_line.price_unit, 5.0)

    def test_pricelist_based_on_product(self):
        sale_orden = self.create_sale()
        order_line = sale_orden.order_line[0]
        self.supplierinfo_pricelist.item_ids = [(0, 0, {
            'compute_price': 'formula',
            'base': 'supplierinfo',
            'price_discount': 0,
            'min_quantity': 1.0,
            'applied_on': '1_product',
            'product_tmpl_id': self.product.product_tmpl_id.id,
        })]
        order_line.product_id_change()
        self.assertAlmostEqual(order_line.price_unit, 10.0)

    def test_pricelist_based_on_product_variant(self):
        sale_orden = self.create_sale()
        order_line = sale_orden.order_line[0]
        self.supplierinfo_pricelist.item_ids = [(0, 0, {
            'compute_price': 'formula',
            'base': 'supplierinfo',
            'price_discount': -25,
            'min_quantity': 1.0,
            'applied_on': '0_product_variant',
            'product_id': self.product.id,
        })]
        order_line.product_id_change()
        self.assertAlmostEqual(order_line.price_unit, 12.5)

    def test_pricelist_min_quantity(self):
        sale_orden = self.create_sale()
        order_line = sale_orden.order_line[0]
        self.supplierinfo_pricelist.item_ids = [(0, 0, {
            'compute_price': 'formula',
            'base': 'supplierinfo',
            'price_discount': 25,
            'min_quantity': 5.0,
            'applied_on': '0_product_variant',
            'product_id': self.product.id,
        })]
        order_line.product_uom_qty = 5.0
        order_line.product_id_change()
        self.assertAlmostEqual(order_line.price_unit, 37.5)

    def test_pricelist_dates(self):
        """ Test pricelist and supplierinfo dates """
        sale_orden = self.create_sale()
        order_line = sale_orden.order_line[0]
        self.supplierinfo_pricelist.item_ids.unlink()
        self.supplierinfo_pricelist.item_ids = [(0, 0, {
            'compute_price': 'formula',
            'base': 'supplierinfo',
            'price_discount': 25,
            'min_quantity': 1.0,
            'applied_on': '0_product_variant',
            'product_id': self.product.id,
            'date_start': '2018-12-31',
            'date_end': '2018-12-31',
        })]
        self.product.seller_ids.write({
            'date_start': '2018-12-31',
            'date_end': '2018-12-31',
        })
        order_line.product_id_change()
        self.assertAlmostEqual(order_line.price_unit, 7.5)
        order_line.unlink()
        item = self.supplierinfo_pricelist.item_ids[0]
        item.date_start = '2018-12-01'
        item.date_end = '2018-12-01'
        order_line = self.env['sale.order.line'].create({
            'order_id': sale_orden.id,
            'product_id': self.product.id,
        })
        order_line.product_id_change()
        # Not supplierinfo pricelist is applied, but public pricelist
        self.assertAlmostEqual(order_line.price_unit, 1.0)
        self.assertAlmostEqual(self.product.lst_price, 1.0)
        item.date_start = False
        item.date_end = False
        self.product.seller_ids[0].date_start = '2018-12-31'
        self.product.seller_ids[0].date_end = '2018-12-31'
        self.product.seller_ids[1].date_start = '2018-12-01'
        self.product.seller_ids[1].date_end = '2018-12-01'
        order_line.unlink()
        order_line = self.env['sale.order.line'].create({
            'order_id': sale_orden.id,
            'product_id': self.product.id,
            'product_uom_qty': 5.0,
        })
        item.min_quantity = 5.0
        order_line.product_id_change()
        self.assertAlmostEqual(order_line.price_unit, 37.5)
        self.product.seller_ids[0].date_start = '2018-12-01'
        self.product.seller_ids[0].date_end = '2018-12-01'
        self.product.seller_ids[1].date_start = '2018-12-31'
        self.product.seller_ids[1].date_end = '2018-12-31'
        order_line.unlink()
        order_line = self.env['sale.order.line'].create({
            'order_id': sale_orden.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
        })
        item.min_quantity = 1.0
        order_line.product_id_change()
        self.assertAlmostEqual(order_line.price_unit, 7.5)
