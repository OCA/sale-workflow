# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY
from odoo.tools import float_compare
from odoo.addons.product.tests.test_product_pricelist\
    import TestProductPricelist as _TestProductPricelist


class TestPricelistIndexedPrice(_TestProductPricelist):
    # keep standard tests to be sure the module doesn't mess up anything there

    def test_20_pricelist_indexed_price(self):
        # first generate an index on our pricelist
        pricelist = self.env.ref('pricelist_indexed_price.demo_pricelist')
        self.env['product.pricelist.index.generator'].with_context(
            active_model='product.pricelist',
            active_id=pricelist.id,
        ).create({
            'date_start': datetime.now() + relativedelta(month=1, day=1),
            'date_end': datetime.now() + relativedelta(month=12, day=31),
            'index_start': 100,
            'index_step': 5,
            'frequency': MONTHLY,
        }).action_generate()
        self.assertEqual(len(pricelist.item_ids), 12)
        # a service in the standard price list (see demo data)
        product = self.env.ref('product.product_product_2_product_template')
        self.assertFalse(float_compare(
            product.with_context(
                pricelist=self.env.ref('product.list0').id,
                date=datetime.now() + relativedelta(month=3, day=1)
            ).price,
            product.list_price * 1.1,
            precision_digits=self.env['decimal.precision']
            .precision_get('Product Price'),
        ))
