# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestProductMarginClassification(common.TransactionCase):

    def setUp(self):
        super(TestProductMarginClassification, self).setUp()
        self.too_expensive_product = self.env.ref(
            'product_margin_classification.too_expensive_product')
        self.price_precision =\
            self.env['decimal.precision'].precision_get('Product Price')
        self.classification_big_margin = self.env.ref(
            'product_margin_classification.classification_big_margin')

    def test_01_product_use_theoretical_price(self):
        """Apply a 50% Markup (with rounding method) for a product with
        a standard price of 100. The result should be 149.95
        ((100 * 1 + (50 / 100)) - 0.05)"""
        self.too_expensive_product.use_theoretical_price()

        new_price = round(
            self.too_expensive_product.list_price, self.price_precision)

        self.assertEquals(new_price, 149.95)

    def test_02_margin_apply_theoretical_price(self):
        """ Apply a margin for all the products of margin classification"""
        self.classification_big_margin.apply_theoretical_price()

        self.assertEquals(
            self.classification_big_margin.template_different_price_qty, 0)
