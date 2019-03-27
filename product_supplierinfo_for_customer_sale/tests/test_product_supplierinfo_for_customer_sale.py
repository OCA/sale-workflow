# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common


class TestProductSupplierinfoForCustomerSale(common.TransactionCase):

    def setUp(self):
        super(TestProductSupplierinfoForCustomerSale, self).setUp()
        self.supplierinfo_model = self.env['product.supplierinfo']
        self.pricelist_item_model = self.env['product.pricelist.item']
        self.pricelist_model = self.env['product.pricelist']
        self.customer = self._create_customer('customer1')
        self.product = self.env.ref('product.product_product_4')
        self.supplierinfo = self._create_supplierinfo(
            'customer', self.customer, self.product)
        self.pricelist = self._create_pricelist(
            'Test Pricelist', self.product)
        self.company = self.env.ref('base.main_company')

    def _create_customer(self, name):
        """Create a Partner."""
        return self.env['res.partner'].create({
            'name': name,
            'email': 'example@yourcompany.com',
            'customer': True,
            'phone': 123456,
        })

    def _create_supplierinfo(self, supplierinfo_type, partner, product):
        return self.supplierinfo_model.create({
            'name': partner.id,
            'product_id': product.id,
            'product_name': 'product4',
            'product_code': '00001',
            'supplierinfo_type': supplierinfo_type,
            'price': 100.0,
            'min_qty': 15.0,
        })

    def _create_pricelist(self, name, product):
        return self.pricelist_model.create({
            'name': name,
            'currency_id': self.env.ref('base.USD').id,
            'item_ids': [(0, 0, {
                'applied_on': '0_product_variant',
                'product_id': product.id,
                'compute_price': 'formula',
                'base': 'partner',
            })],
        })

    def test_product_supplierinfo_for_customer_sale(self):
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'pricelist_id': self.pricelist.id,
        })
        line = self.env['sale.order.line'].create({
            'product_id': self.product.id,
            'order_id': so.id,
        })
        line.product_id_change()

        self.assertEqual(
            line.product_customer_code, self.supplierinfo.product_code,
            "Error: Customer product code was not passed to sale order line")
        self.assertEqual(
            line.product_uom_qty, self.supplierinfo.min_qty,
            "Error: Min qty was not passed to the sale order line")
