# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date

from odoo import fields, models
from odoo.osv.expression import AND


class ProductPricelistCache(models.Model):

    _inherit = "product.pricelist.cache"

    date_start = fields.Date()
    date_end = fields.Date()

    @classmethod
    def _get_cache_sql_order(cls):
        return (
            "pricelist_id, product_id, "
            "date_start DESC NULLS LAST, date_end DESC NULLS LAST"
        )

    def _get_item_domain_date(self):
        return [
            "|",
            ("date_start", "!=", False),
            ("date_end", "!=", False),
        ]

    def _get_item_product_domain(self):
        return [
            ("product_id", "=", 17),
            ("applied_on", "=", "0_product_variant"),
        ]

    def _get_global_domain(self):
        # TODO Is it used?
        return [
            ("applied_on", "=", "3_global"),
        ]

    def _get_product_item_domain(self):
        date_domain = self._get_item_domain_date()
        product_domain = self._get_item_product_domain()
        return AND([date_domain, product_domain])

    def _get_items(self):
        domain = self._get_product_item_domain()
        items = self.env["product.pricelist.item"].search(domain)
        return items.ids

    def _get_prices_from_product_items(self, item_ids):
        res = set()
        item_model = self.env["product.pricelist.item"]
        items = item_model.browse(item_ids)
        for item in items:
            # in order to retrieve a price for a given pricelist, odoo tries to find
            # items for a given date.
            # If multiple items are found, they are ultimately sorted by id.
            # It means that if multiple item's date ranges are overlapping, the one
            # having the biggest id will be used.
            #                                   now
            #                                    v
            # item1 : -------- 42.0€, id 7 --------->
            # item2 :                   <------12.0€, id 8------>
            # item3 :                          <-----------40.0€, id 5-------------
            # The price returned by odoo in such case will be 12.0€.
            # In such case, for this product, we have to store 3 prices at dates that
            # are not those stored on the pricelist items
            #
            # We could also have this case
            # item1 : -------- 42.0€, id 7: all the time --------------------------
            # item2 : ----------12.0€ id 5 ----------------->
            # item3 :                             <--------------10.0€, id 6-------
            # In such case, 42.0€ would always be returned by odoo,
            # and the items 2 and 3 are useless.
            overlaps = item._get_orverlap_items(items)
            if overlaps:
                date_ranges = overlaps._get_not_overlapping_date_ranges()
                for date_start, date_end in date_ranges:
                    date = date_start or date_end
                    pricelist = item.pricelist_id
                    product = item.product_id
                    price_values = pricelist._get_product_prices(product.ids, date)
                    prices = price_values[product.id]
                    for price, __, __ in prices:
                        values = (
                            product.id,
                            pricelist.id,
                            price,
                            date_start or None,
                            date_end or None,
                        )
                        res.add(values)
            else:
                values = item._get_item_values()
                pricelist = self.env["product.pricelist"].browse(values["pricelist_id"])
                date = values["date_to_check"]
                product_id = values["product_id"]
                price_values = pricelist._get_product_prices([product_id], date)
                prices = price_values[product_id]
                for price, __, __ in prices:
                    values = (
                        product_id,
                        pricelist.id,
                        price,
                        values.get("date_start"),
                        values.get("date_end"),
                    )
                    res.add(values)
        return res

    def _get_values(self):
        item_ids = self._get_items()
        return self._get_prices_from_product_items(item_ids)

    def _create_cache_with_date(self):
        values = self._get_values()
        if values:
            self._create_cache_records(values)

    def create_full_cache(self):
        super().create_full_cache()
        # As `pricelist_cache` already stored prices for all items as of today,
        # We need to store the informations about dates.
        # We might currently be in a pricelist item date range, or one could start in
        # a few days…
        self._create_cache_with_date()

    def _get_create_columns(self):
        res = super()._get_create_columns()
        return res + ["date_start", "date_end"]

    def _get_cached_price_select_clause(self):
        return """SELECT DISTINCT ON (pricelist_id, product_id) id"""

    def _get_cached_price_where_conditions(self):
        res = super()._get_cached_price_where_conditions()
        res.extend(
            [
                "(date_start IS NULL OR date_start <= %(at_date)s)",
                "(date_end IS NULL OR date_end >= %(at_date)s)",
            ]
        )
        return res

    def _get_cached_price_order_clause(self):
        order = self._get_cache_sql_order()
        return f"""ORDER BY {order}"""

    def _get_cached_price_query_items(self):
        res = super()._get_cached_price_query_items()
        res.append(self._get_cached_price_order_clause())
        return res

    def _get_cached_price_args(self, pricelist_id, product_ids, at_date=None):
        res = super()._get_cached_price_args(pricelist_id, product_ids)
        if not at_date:
            at_date = date.today()
        res.update(at_date=str(at_date))
        return res
