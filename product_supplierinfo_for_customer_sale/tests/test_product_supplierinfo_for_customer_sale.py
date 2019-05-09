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
        self.product_variant_1 = self.env.ref('product.product_product_4b')
        self.product_variant_2 = self.env.ref('product.product_product_4c')
        self.supplierinfo = self._create_supplierinfo(
            'customer', self.customer, self.product)
        self.pricelist = self._create_pricelist(
            'Test Pricelist', self.product)
        self.company = self.env.ref('base.main_company')
        self._create_supplierinfo(
            'customer', self.customer, self.product_variant_1)
        self._create_supplierinfo(
            'customer', self.customer, self.product_variant_2,
            empty_variant=True)
        self.product_template = self.env['product.template'].create({
            'name': 'product wo variants'
        })
        self._create_supplierinfo(
            'customer', self.customer,
            self.product_template.product_variant_ids[:1],
            empty_variant=True)
        self.pricelist_template = self._create_pricelist(
            'Test Pricelist Template',
            self.product_template.product_variant_ids[:1])

    def _create_customer(self, name):
        """Create a Partner."""
        return self.env['res.partner'].create({
            'name': name,
            'email': 'example@yourcompany.com',
            'customer': True,
            'phone': 123456,
        })

    def _create_supplierinfo(self, supplierinfo_type, partner, product,
                             empty_variant=False):
        vals = {
            'name': partner.id,
            'product_id': product.id,
            'product_name': 'product4',
            'product_code': '00001',
            'supplierinfo_type': supplierinfo_type,
            'price': 100.0,
            'min_qty': 15.0,
        }
        if empty_variant:
            vals.pop('product_id', None)
            vals['product_tmpl_id'] = product.product_tmpl_id.id
        return self.supplierinfo_model.create(vals)

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

    def test_product_supplierinfo_for_customer_sale_variant(self):
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'pricelist_id': self.pricelist.id,
        })
        line = self.env['sale.order.line'].create({
            'product_id': self.product_variant_1.id,
            'order_id': so.id,
        })
        line.product_id_change()
        self.assertEqual(
            line.product_customer_code, self.supplierinfo.product_code,
            "Error: Customer product code was not passed to sale order line")

    def test_product_supplierinfo_for_customer_sale_template(self):
        supplierinfo = self._create_supplierinfo('customer', self.customer,
                                                 self.product_variant_2)
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'pricelist_id': self.pricelist.id,
        })
        line = self.env['sale.order.line'].create({
            'product_id': self.product_variant_2.id,
            'order_id': so.id,
        })
        line.product_id_change()
        self.assertEqual(
            line.product_customer_code, supplierinfo.product_code,
            "Error: Customer product code was not passed to sale order line")
        # Test with product without variants
        so2 = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'pricelist_id': self.pricelist_template.id,
        })
        line2 = self.env['sale.order.line'].create({
            'product_id': self.product_template.product_variant_ids.id,
            'order_id': so2.id,
        })
        line2.product_id_change()
        self.assertEqual(
            line2.product_customer_code, supplierinfo.product_code,
            "Error: Customer product code was not passed to sale order line")

    def test_product_supplierinfo_for_customer_sale_variant_wo_template(self):
        supplierinfo = self._create_supplierinfo(
            'customer', self.customer, self.product_variant_2,
            empty_variant=True)
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'pricelist_id': self.pricelist.id,
        })
        line = self.env['sale.order.line'].create({
            'product_id': self.product_variant_2.id,
            'order_id': so.id,
        })
        line.product_id_change()
        self.assertEqual(
            line.product_customer_code, supplierinfo.product_code,
            "Error: Customer product code was not passed to sale order line")
