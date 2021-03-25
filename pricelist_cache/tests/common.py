# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from functools import wraps

from odoo.tests import SavepointCase

LIST_PRICES_MAPPING = {
    "pricelist_cache.list0": [
        {"id": 17, "price": 100.0},
        {"id": 18, "price": 79.0},
        {"id": 19, "price": 100.0},
        {"id": 20, "price": 47.0},
    ],
    "pricelist_cache.list1": [
        {"id": 17, "price": 75.0},
        {"id": 18, "price": 79.0},
        {"id": 19, "price": 100.0},
        {"id": 20, "price": 47.0},
    ],
    "pricelist_cache.list2": [
        {"id": 17, "price": 50.0},
        {"id": 18, "price": 79.0},
        {"id": 19, "price": 100.0},
        {"id": 20, "price": 47.0},
    ],
    "pricelist_cache.list3": [
        {"id": 17, "price": 25.0},
        {"id": 18, "price": 79.0},
        {"id": 19, "price": 100.0},
        {"id": 20, "price": 47.0},
    ],
    "pricelist_cache.list4": [
        {"id": 17, "price": 15.0},
        {"id": 18, "price": 50.0},
        {"id": 19, "price": 100.0},
        {"id": 20, "price": 47.0},
    ],
    "pricelist_cache.list5": [
        {"id": 17, "price": 45.0},
        {"id": 18, "price": 99.0},
        {"id": 19, "price": 120.0},
        {"id": 20, "price": 67.0},
    ],
}


def check_duplicates(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        duplicates_query = """
            SELECT product_id, pricelist_id, count(*)
            FROM product_pricelist_cache
            GROUP BY product_id, pricelist_id
            HAVING count(*) > 1;
        """
        self.env.cr.execute(duplicates_query)
        res = self.env.cr.fetchall()
        self.assertFalse(res)

    return wrapper


class TestPricelistCacheCommon(SavepointCase):
    @classmethod
    def setUpClassBaseCache(cls):
        cls.cache_model.cron_reset_pricelist_cache()

    @classmethod
    def set_currency(cls):
        """Sets currency everywhere, as the sale dependency breaks every unit test."""
        usd = cls.env.ref("base.USD")
        cls.env.user.company_id.currency_id = usd
        cls.products.write({"currency_id": usd.id})
        cls.lists.write({"currency_id": usd.id})
        cls.pricelist_items.write({"currency_id": usd.id})

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                test_queue_job_no_delay=True,
            )
        )
        # Odoo does not seems to register hooks by itself when tests are run
        # the following line registers them explicitely
        cls.env["base.automation"]._register_hook()
        cls.cache_model = cls.env["product.pricelist.cache"]
        # root pricelists
        cls.list0 = cls.env.ref("pricelist_cache.list0")
        # child 1, based on list0
        cls.list1 = cls.env.ref("pricelist_cache.list1")
        # child 2, based on list1
        cls.list2 = cls.env.ref("pricelist_cache.list2")
        # child 3, based on list2
        cls.list3 = cls.env.ref("pricelist_cache.list3")
        # child 4, based on list0
        cls.list4 = cls.env.ref("pricelist_cache.list4")
        # factor list 5, based on list3
        cls.list5 = cls.env.ref("pricelist_cache.list5")
        # TODO ugly
        cls.lists = cls.env["product.pricelist"].browse(
            [
                cls.list0.id,
                cls.list1.id,
                cls.list2.id,
                cls.list3.id,
                cls.list4.id,
                cls.list5.id,
            ]
        )
        # products
        cls.p6 = cls.env.ref("product.product_product_6")
        cls.p7 = cls.env.ref("product.product_product_7")
        cls.p8 = cls.env.ref("product.product_product_8")
        # P9 not in any pricelist
        cls.p9 = cls.env.ref("product.product_product_9")
        # TODO ugly
        cls.products = cls.env["product.product"].browse(
            [cls.p6.id, cls.p7.id, cls.p8.id, cls.p9.id]
        )
        cls.pricelist_items = cls.env["product.pricelist.item"]
        cls.pricelist_items |= cls.list0.item_ids
        cls.pricelist_items |= cls.list1.item_ids
        cls.pricelist_items |= cls.list2.item_ids
        cls.pricelist_items |= cls.list3.item_ids
        cls.pricelist_items |= cls.list4.item_ids
        cls.set_currency()
        cls.setUpClassBaseCache()
        cls.partner = cls.env.ref("base.res_partner_12")
