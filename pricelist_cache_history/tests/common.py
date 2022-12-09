# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.pricelist_cache.tests.common import TestPricelistCacheCommon


class TestPricelistCacheHistoryCommonCase(TestPricelistCacheCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setUpClassVars()
        cls.setUpClassItems()

    @classmethod
    def setUpClassVars(cls):
        cls.product = cls.p6
        cls.item_model = cls.env["product.pricelist.item"]
        cls.list_model = cls.env["product.pricelist"]

    @classmethod
    def setUpClassItems(cls):
        cls.list = cls.env.ref("pricelist_cache_history.list_with_dates")
        cls.ending_list = cls.env.ref("pricelist_cache_history.list_with_ending_dates")
        cls.formula_list = cls.env.ref("pricelist_cache_history.list_with_formulas")
        cls.item1 = cls.env.ref("pricelist_cache_history.item1")
        cls.item2 = cls.env.ref("pricelist_cache_history.item2")
        cls.item3 = cls.env.ref("pricelist_cache_history.item3")
        cls.item4 = cls.env.ref("pricelist_cache_history.item4")
        cls.items = cls.item1 | cls.item2 | cls.item3 | cls.item4
