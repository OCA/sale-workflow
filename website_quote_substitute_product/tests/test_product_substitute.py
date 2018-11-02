from odoo.tests import common


class TestProductSubstitute(common.TransactionCase):

    def setUp(self):
        super(TestProductSubstitute, self).setUp()

        self.so_model = self.env['sale.order']
        self.po_line_model = self.env['sale.order.line']
        self.res_partner_model = self.env['res.partner']
        self.product_model = self.env['product.product']
        self.product_uom_model = self.env['product.uom']
        self.pricelist_model = self.env['product.pricelist']
        self.partner = self.env.ref('base.res_partner_1')
        self.product1 = self.product_model.create({
            'name': 'Product A',
            'type': 'product',
            'lst_price': 1,
            'categ_id': self.env.ref('product.product_category_all').id,
        })
        self.product2 = self.product_model.create({
            'name': 'Product B',
            'type': 'product',
            'lst_price': 2,
            'categ_id': self.env.ref('product.product_category_all').id,
        })
        self.product3 = self.product_model.create({
            'name': 'Product C',
            'type': 'product',
            'lst_price': 3,
            'categ_id': self.env.ref('product.product_category_all').id,
        })
        self.product4 = self.product_model.create({
            'name': 'Product D',
            'type': 'product',
            'lst_price': 4,
            'categ_id': self.env.ref('product.product_category_all').id,
        })

    def test_subsitute_product(self):
        """ Test substitute product button."""
        uom_id = self.product_uom_model.search([('name', '=', 'Unit(s)')])[0]
        pricelist = self.pricelist_model.search([
            ('name', '=', 'Public Pricelist')])[0]

        so_vals = {
            'partner_id': self.partner.id,
            'pricelist_id': pricelist.id,
            'order_line': [
                (0, 0, {
                    'name': self.product2.name,
                    'product_id': self.product2.id,
                    'product_uom_qty': 1.0,
                    'product_uom': uom_id.id,
                    'price_unit': 121.0
                })
            ],

        }

        so = self.so_model.create(so_vals)
        so.write({
            'order_line': [
                (0, 0, {
                    'name': self.product4.name,
                    'product_id': self.product4.id,
                    'product_uom_qty': 1.0,
                    'product_uom': uom_id.id,
                    'price_unit': 4
                })
            ]
        })
        so.write({
            'product_substitute_ids': [
                (0, 0, {
                    'sale_order_line_id': so.order_line[0].id,
                    'product_substitute_id': self.product2.id,
                })
            ]
        })
        so.write({
            'product_substitute_ids': [
                (0, 0, {
                    'sale_order_line_id': so.order_line[0].id,
                    'product_substitute_id': self.product3.id,
                })
            ]
        })
        so.product_substitute_ids[0]._onchange_substitute_product()
        so.product_substitute_ids[1]._onchange_substitute_product()
        so.product_substitute_ids[0].sale_order_line_id = so.order_line[1].id
        so.product_substitute_ids[0]._onchange_product_id()
        so.product_substitute_ids[0].sale_order_line_id = so.order_line[0].id
        so.product_substitute_ids[0]._onchange_product_id()
        so.product_substitute_ids[0].button_substitute_product()

        self.assertEqual(
            so.order_line[0].product_id.id,
            self.product2.id,
            'Products are not changed proper.')
