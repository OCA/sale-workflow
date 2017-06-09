# -*- coding: utf-8 -*-
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestSaleLinePricePropertiesBased(TransactionCase):

    def setUp(self):
        super(TestSaleLinePricePropertiesBased, self).setUp()
        self.partner = self.env.ref('base.res_partner_3')
        # use product for which is set price_formula_id
        product = self.env.ref('product.product_product_7')
        self.so = self.env['sale.order'].create({
            'partner_id': self.partner.id
        })

        length_5 = self.env.ref('sale_properties_easy_creation.length_5')
        width_1 = self.env.ref('sale_properties_easy_creation.width_1')
        self.sol = self.env['sale.order.line'].create({
            'name': '/',
            'order_id': self.so.id,
            'product_id': product.id,
        })
        self.sol.property_ids = [length_5.id, width_1.id]

    def test_price_property_ids_changed(self):
        self.sol.price_property_ids_changed()
        # according to sale_properties_easy_creation.area_formula
        # price_unit should be (length_5 * width_1) / 2
        self.assertEqual(self.sol.price_unit, 2.5)
