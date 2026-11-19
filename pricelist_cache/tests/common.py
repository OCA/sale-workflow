# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from functools import wraps

from odoo.addons.base.tests.common import BaseCommon

LIST_PRICES_MAPPING = {
    "pricelist_cache.list0": {
        "product.product_product_6": 100.0,
        "product.product_product_7": 15.8,
        "product.product_product_8": 100.0,
        "product.product_product_9": 47.0,
    },
    "pricelist_cache.list1": {
        "product.product_product_6": 75.0,
        "product.product_product_7": 15.8,
        "product.product_product_8": 100.0,
        "product.product_product_9": 47.0,
    },
    "pricelist_cache.list2": {
        "product.product_product_6": 50.0,
        "product.product_product_7": 15.8,
        "product.product_product_8": 100.0,
        "product.product_product_9": 47.0,
    },
    "pricelist_cache.list3": {
        "product.product_product_6": 25.0,
        "product.product_product_7": 15.8,
        "product.product_product_8": 100.0,
        "product.product_product_9": 47.0,
    },
    "pricelist_cache.list4": {
        "product.product_product_6": 15.0,
        "product.product_product_7": 50.0,
        "product.product_product_8": 100.0,
        "product.product_product_9": 47.0,
    },
    "pricelist_cache.list5": {
        "product.product_product_6": 45.0,
        "product.product_product_7": 35.8,
        "product.product_product_8": 120.0,
        "product.product_product_9": 67.0,
    },
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


class TestPricelistCacheCommon(BaseCommon):
    @classmethod
    def setUpClassBaseCache(cls):
        cls.cache_model.cron_reset_pricelist_cache()
        cls.env["product.pricelist"].invalidate_model(["is_pricelist_cache_available"])

    @classmethod
    def set_currency(cls):
        """Sets currency everywhere, as the sale dependency breaks every unit test."""
        usd = cls.env.ref("base.USD")
        cls.env.user.company_id.currency_id = usd
        cls.products.write({"currency_id": usd.id})
        cls.lists.write({"currency_id": usd.id})
        cls.pricelist_items.write({"currency_id": usd.id})

    @classmethod
    def _create_xmlid(cls, record, xmlid):
        module, name = xmlid.split(".")
        existing = cls.env["ir.model.data"].search(
            [("module", "=", module), ("name", "=", name)]
        )
        if not existing:
            cls.env["ir.model.data"].create(
                {
                    "module": module,
                    "name": name,
                    "model": record._name,
                    "res_id": record.id,
                    "noupdate": True,
                }
            )

    @classmethod
    def _ensure_test_data(cls):
        cls.partner = cls.env.ref("base.res_partner_12", raise_if_not_found=False)
        if not cls.partner:
            cls.partner = cls.env["res.partner"].create({"name": "Azure Interior"})
            cls._create_xmlid(cls.partner, "base.res_partner_12")

        cls.p6 = cls.env.ref("product.product_product_6", raise_if_not_found=False)
        if not cls.p6:
            cls.p6 = cls.env["product.product"].create(
                {
                    "name": "Large Cabinet",
                    "list_price": 320.0,
                    "standard_price": 800.0,
                    "type": "consu",
                }
            )
            cls._create_xmlid(cls.p6, "product.product_product_6")

        cls.p7 = cls.env.ref("product.product_product_7", raise_if_not_found=False)
        if not cls.p7:
            cls.p7 = cls.env["product.product"].create(
                {
                    "name": "Storage Box",
                    "list_price": 15.8,
                    "standard_price": 14.0,
                    "type": "consu",
                }
            )
            cls._create_xmlid(cls.p7, "product.product_product_7")

        cls.p8 = cls.env.ref("product.product_product_8", raise_if_not_found=False)
        if not cls.p8:
            cls.p8 = cls.env["product.product"].create(
                {
                    "name": "Large Desk",
                    "list_price": 1799.0,
                    "standard_price": 1299.0,
                    "type": "consu",
                }
            )
            cls._create_xmlid(cls.p8, "product.product_product_8")

        cls.p9 = cls.env.ref("product.product_product_9", raise_if_not_found=False)
        if not cls.p9:
            cls.p9 = cls.env["product.product"].create(
                {
                    "name": "Pedal Bin",
                    "list_price": 47.0,
                    "standard_price": 10.0,
                    "type": "consu",
                }
            )
            cls._create_xmlid(cls.p9, "product.product_product_9")

        cls.list0 = cls.env.ref("pricelist_cache.list0", raise_if_not_found=False)
        if not cls.list0:
            cls.list0 = cls.env["product.pricelist"].create({"name": "Pricelist 0"})
            cls._create_xmlid(cls.list0, "pricelist_cache.list0")

            item2 = cls.env["product.pricelist.item"].create(
                {
                    "pricelist_id": cls.list0.id,
                    "applied_on": "0_product_variant",
                    "product_id": cls.p6.id,
                    "base": "list_price",
                    "fixed_price": 100.0,
                }
            )
            cls._create_xmlid(item2, "pricelist_cache.item2")

            item3 = cls.env["product.pricelist.item"].create(
                {
                    "pricelist_id": cls.list0.id,
                    "applied_on": "0_product_variant",
                    "product_id": cls.p8.id,
                    "base": "list_price",
                    "fixed_price": 100.0,
                }
            )
            cls._create_xmlid(item3, "pricelist_cache.item3")

        cls.list1 = cls.env.ref("pricelist_cache.list1", raise_if_not_found=False)
        if not cls.list1:
            cls.list1 = cls.env["product.pricelist"].create(
                {
                    "name": "Pricelist 1",
                    "sequence": 2,
                }
            )
            cls._create_xmlid(cls.list1, "pricelist_cache.list1")

            item4 = cls.env["product.pricelist.item"].create(
                {
                    "pricelist_id": cls.list1.id,
                    "applied_on": "3_global",
                    "compute_price": "formula",
                    "base": "pricelist",
                    "base_pricelist_id": cls.list0.id,
                }
            )
            cls._create_xmlid(item4, "pricelist_cache.item4")

            item5 = cls.env["product.pricelist.item"].create(
                {
                    "pricelist_id": cls.list1.id,
                    "applied_on": "0_product_variant",
                    "product_id": cls.p6.id,
                    "base": "list_price",
                    "fixed_price": 75.0,
                }
            )
            cls._create_xmlid(item5, "pricelist_cache.item5")

        cls.list2 = cls.env.ref("pricelist_cache.list2", raise_if_not_found=False)
        if not cls.list2:
            cls.list2 = cls.env["product.pricelist"].create(
                {
                    "name": "Pricelist 2",
                    "sequence": 3,
                }
            )
            cls._create_xmlid(cls.list2, "pricelist_cache.list2")

            item6 = cls.env["product.pricelist.item"].create(
                {
                    "pricelist_id": cls.list2.id,
                    "applied_on": "3_global",
                    "compute_price": "formula",
                    "base": "pricelist",
                    "base_pricelist_id": cls.list1.id,
                }
            )
            cls._create_xmlid(item6, "pricelist_cache.item6")

            item7 = cls.env["product.pricelist.item"].create(
                {
                    "pricelist_id": cls.list2.id,
                    "applied_on": "0_product_variant",
                    "product_id": cls.p6.id,
                    "base": "list_price",
                    "fixed_price": 50.0,
                    "date_start": "2021-03-01",
                    "date_end": "2021-04-01",
                }
            )
            cls._create_xmlid(item7, "pricelist_cache.item7")

        cls.list3 = cls.env.ref("pricelist_cache.list3", raise_if_not_found=False)
        if not cls.list3:
            cls.list3 = cls.env["product.pricelist"].create(
                {
                    "name": "Pricelist 3",
                    "sequence": 4,
                }
            )
            cls._create_xmlid(cls.list3, "pricelist_cache.list3")

            item8 = cls.env["product.pricelist.item"].create(
                {
                    "pricelist_id": cls.list3.id,
                    "applied_on": "3_global",
                    "compute_price": "formula",
                    "base": "pricelist",
                    "base_pricelist_id": cls.list2.id,
                }
            )
            cls._create_xmlid(item8, "pricelist_cache.item8")

            item9 = cls.env["product.pricelist.item"].create(
                {
                    "pricelist_id": cls.list3.id,
                    "applied_on": "0_product_variant",
                    "product_id": cls.p6.id,
                    "base": "list_price",
                    "fixed_price": 25.0,
                }
            )
            cls._create_xmlid(item9, "pricelist_cache.item9")

        cls.list4 = cls.env.ref("pricelist_cache.list4", raise_if_not_found=False)
        if not cls.list4:
            cls.list4 = cls.env["product.pricelist"].create(
                {
                    "name": "Pricelist 4",
                    "sequence": 5,
                }
            )
            cls._create_xmlid(cls.list4, "pricelist_cache.list4")

            item10 = cls.env["product.pricelist.item"].create(
                {
                    "pricelist_id": cls.list4.id,
                    "applied_on": "3_global",
                    "compute_price": "formula",
                    "base": "pricelist",
                    "base_pricelist_id": cls.list0.id,
                }
            )
            cls._create_xmlid(item10, "pricelist_cache.item10")

            item11 = cls.env["product.pricelist.item"].create(
                {
                    "pricelist_id": cls.list4.id,
                    "applied_on": "0_product_variant",
                    "product_id": cls.p6.id,
                    "base": "list_price",
                    "fixed_price": 15.0,
                }
            )
            cls._create_xmlid(item11, "pricelist_cache.item11")

            item12 = cls.env["product.pricelist.item"].create(
                {
                    "pricelist_id": cls.list4.id,
                    "applied_on": "0_product_variant",
                    "product_id": cls.p7.id,
                    "base": "list_price",
                    "fixed_price": 50.0,
                }
            )
            cls._create_xmlid(item12, "pricelist_cache.item12")

        cls.list5 = cls.env.ref("pricelist_cache.list5", raise_if_not_found=False)
        if not cls.list5:
            cls.list5 = cls.env["product.pricelist"].create(
                {
                    "name": "Pricelist 5",
                    "sequence": 6,
                }
            )
            cls._create_xmlid(cls.list5, "pricelist_cache.list5")

            item13 = cls.env["product.pricelist.item"].create(
                {
                    "pricelist_id": cls.list5.id,
                    "applied_on": "3_global",
                    "compute_price": "formula",
                    "base": "pricelist",
                    "base_pricelist_id": cls.list3.id,
                    "price_surcharge": 20.0,
                }
            )
            cls._create_xmlid(item13, "pricelist_cache.item13")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                queue_job__no_delay=True,
            )
        )
        cls.cache_model = cls.env["product.pricelist.cache"]
        cls._ensure_test_data()
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

    def _flush_cache(self):
        self.cache_model.flush_pricelist_cache()
        self.env["res.partner"].invalidate_model(["is_pricelist_cache_available"])
        self.env["product.pricelist"].invalidate_model(["is_pricelist_cache_available"])

    def _update_cache(self, pricelist_ids=None, product_ids=None):
        self.cache_model.update_product_pricelist_cache(
            product_ids=product_ids, pricelist_ids=pricelist_ids
        )
        self.env["res.partner"].invalidate_model(["is_pricelist_cache_available"])
        self.env["product.pricelist"].invalidate_model(["is_pricelist_cache_available"])

    def assert_cache_available(self, lists):
        self.assertTrue(all(lists.mapped("is_pricelist_cache_available")))

    def assert_cache_computed(self, lists):
        self.assertTrue(all(lists.mapped("is_pricelist_cache_computed")))

    def assert_cache_not_available(self, lists):
        self.assertFalse(any(lists.mapped("is_pricelist_cache_available")))

    def assert_cache_not_computed(self, lists):
        self.assertFalse(any(lists.mapped("is_pricelist_cache_computed")))
