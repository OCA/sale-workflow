# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from psycopg2.extras import execute_values

from odoo import fields, models, tools


class ProductPricelistCache(models.Model):

    # 1) item with formula is based on dates, whether it has date_start or date_end
    #    because, if parent list changes prices while formula item is active,
    #    then the price changes accordingly
    # 2) pricelist cache should be overriden so it only computes base prices
    #    a base price is, for a couple (pricelist, product):
    #      - fixed price coming from a item with no dates
    #      - formula price where no other item (from parents and current pricelist)
    #        alters the price.
    #    if no base price is found: do not cache anything
    # 3)

    _inherit = "product.pricelist.cache"

    date_start = fields.Date()
    date_end = fields.Date()

    def _create_cache_with_date__get_create_columns(self):
        res = self._create_cache_records__get_create_columns()
        return res + ["date_start", "date_end"]

    def _create_cache_with_date__get_insert_clause(self):
        """Returns the INSERT clause template for the INSERT query."""
        template = "INSERT INTO product_pricelist_cache ({columns})"
        columns = self._create_cache_with_date__get_create_columns()
        sql_columns = ", ".join(columns)
        return template.format(columns=sql_columns)

    def _create_cache_records__get_values_clause(self):
        """Returns the VALUES clause template for the INSERT SQL query."""
        return "VALUES %s"

    def _create_cache_with_date__get_sql_template_parts(self):
        """Returns all clause templates for the INSERT sql query."""
        return [
            self._create_cache_with_date__get_insert_clause(),
            self._create_cache_records__get_values_clause(),
        ]

    def _create_cache_with_date__get_sql_template(self):
        """Returns the SQL formatted INSERT query template."""
        return "\n".join(self._create_cache_with_date__get_sql_template_parts())

    def _create_cache_with_date__create_cache(self, pricelist_ids):
        pricelists = self.env["product.pricelist"].search([("id", "in", pricelist_ids)])
        raw_values = pricelists._create_cache_with_date__get_raw_values()
        if raw_values:
            sql_template = self._create_cache_with_date__get_sql_template()
            self.flush()
            execute_values(self.env.cr, sql_template, raw_values)
        pricelists.is_pricelist_cache_computed = True

    def _create_cache_with_date(self):
        pricelists = self.env["product.pricelist"].search([])
        pricelist_ids = pricelists.ids
        # Spawn a job every 3 pricelists (reduce the number of jobs created)
        for chunk_ids in tools.misc.split_every(3, pricelist_ids):
            self.with_delay()._create_cache_with_date__create_cache(
                pricelist_ids=chunk_ids
            )

    def create_full_cache(self):
        if self.env.company.pricelist_cache_by_date:
            self._create_cache_with_date()
        else:
            super().create_full_cache()

    def _get_cached_price_args(self, pricelist_id, product_ids, **kwargs):
        args = super()._get_cached_price_args(pricelist_id, product_ids, **kwargs)
        args["at_date"] = kwargs.get("at_date", datetime.now())
        return args

    def _get_cached_price_where_conditions(self):
        conditions = super()._get_cached_price_where_conditions()
        after_date_start = "(date_start IS NULL OR date_start <= %(at_date)s)"
        before_date_end = "(date_end IS NULL OR date_end >= %(at_date)s)"
        conditions.append(f"({after_date_start} AND {before_date_end})")
        return conditions

    def _get_cached_price_query_items(self):
        order_clause = """
            ORDER BY pricelist_id,
                     product_id,
                     date_start ASC NULLS LAST,
                     date_end ASC NULLS LAST
        """
        res = super()._get_cached_price_query_items()
        res.append(order_clause)
        return res

    def _get_cached_price_select_clause(self):
        return """SELECT DISTINCT ON (pricelist_id, product_id) id"""
