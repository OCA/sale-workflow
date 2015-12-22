# -*- coding: utf-8 -*-
# © 2015 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestSaleOrderLineVariantDescription(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderLineVariantDescription, self).setUp()
        self.fiscal_position_model = self.env['account.fiscal.position']
        self.tax_model = self.env['account.tax']
        self.pricelist_model = self.env['product.pricelist']
        self.res_partner_model = self.env['res.partner']
        self.product_tmpl_model = self.env['product.template']
        self.product_model = self.env['product.product']
        self.so_line_model = self.env['sale.order.line']
        self.partner = self.env.ref('base.res_partner_1')

    def test_product_id_change(self):
        pricelist = self.pricelist_model.search(
            [('name', '=', 'Public Pricelist')])[0]
        tax_include = self.tax_model.create(dict(name="Include tax",
                                            type='percent',
                                            amount='0.21',
                                            price_include=True))
        product_tmpl = self.product_tmpl_model.create(
            dict(
                name="Product template", list_price='121',
                taxes_id=[(6, 0, [tax_include.id])]))
        product = self.product_model.create(
            dict(product_tmpl_id=product_tmpl.id,
                 variant_description_sale="Product variant description"))
        fp = self.fiscal_position_model.create(dict(name="fiscal position",
                                                    sequence=1))
        res = self.so_line_model.product_id_change(
            pricelist.id, product.id, partner_id=self.partner.id,
            fiscal_position=fp.id)
        self.assertEqual(
            product.variant_description_sale, res['value']['name'])
