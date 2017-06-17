# -*- coding: utf-8 -*-
# Copyright 2015-2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestSaleOrderLineVariantDescription(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderLineVariantDescription, self).setUp()
        self.fiscal_position_model = self.env['account.fiscal.position']
        self.fiscal_position_tax_model = self.env[
            'account.fiscal.position.tax']
        self.tax_model = self.env['account.tax']
        self.so_model = self.env['sale.order']
        self.po_line_model = self.env['sale.order.line']
        self.res_partner_model = self.env['res.partner']
        self.product_tmpl_model = self.env['product.template']
        self.product_model = self.env['product.product']
        self.product_uom_model = self.env['product.uom']
        self.supplierinfo_model = self.env["product.supplierinfo"]
        self.pricelist_model = self.env['product.pricelist']

    def test_onchange_product_id(self):
        uom_id = self.product_uom_model.search(
            [('name', '=', 'Unit(s)')])[0]
        pricelist = self.pricelist_model.search(
            [('name', '=', 'Public Pricelist')])[0]

        partner_id = self.res_partner_model.create(dict(name="A Boy"))
        tax_include_id = self.tax_model.create(
            dict(name="Include tax",
                 amount='21.00',
                 price_include=True,
                 type_tax_use='sale')
        )

        product_tmpl_id = self.product_tmpl_model.create(
            dict(name="A Product",
                 list_price=121,
                 taxes_id=[(6, 0, [tax_include_id.id])])
        )

        product_id = self.product_model.create(
            dict(product_tmpl_id=product_tmpl_id.id,
                 variant_description_sale="Product variant description"))

        fp_id = self.fiscal_position_model.create(
            dict(name="fiscal position", sequence=1))

        so_vals = {
            'partner_id': partner_id.id,
            'pricelist_id': pricelist.id,
            'fiscal_position_id': fp_id.id,
            'order_line': [
                (0, 0, {
                    'name': product_id.name,
                    'product_id': product_id.id,
                    'product_uom_qty': 1.0,
                    'product_uom': uom_id.id,
                    'price_unit': 121.0
                })
            ]
        }

        so = self.so_model.create(so_vals)

        so_line = so.order_line[0]
        so_line.product_id_change()
        self.assertEqual(
            product_id.variant_description_sale, so_line.name)
