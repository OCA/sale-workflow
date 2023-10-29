# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date, timedelta, datetime

from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _create_cache_with_date__get_values_from_date_ranges(self, product_id, date_ranges):
        self.ensure_one()
        values = []
        for date_start, date_end in date_ranges:
            # We might have a False value (never starting or ending item)
            at_date = date_start or date_end
            product_price = self._get_product_prices([product_id], at_date)
            price = product_price.get(product_id, None)
            if price is not None:
                values.append(
                    (
                        product_id,
                        self.id,
                        price,
                        date_start or None,
                        date_end or None,
                    )
                )
        return values

    def _create_cache_with_date__get_date_items(self, product_id=False):
        if product_id:
            query = """
                SELECT ppi.id
                FROM product_pricelist_item ppi
                JOIN product_product pp
                     ON pp.id = ppi.product_id
                WHERE pp.active = TRUE
                AND ppi.active = TRUE
                AND ppi.pricelist_id = %(pricelist_id)s
                AND (
                    ppi.date_start IS NOT NULL
                    OR ppi.date_end IS NOT NULL
                )
                AND pp.id = %(product_id)s
                AND pp.active = TRUE;
            """
        else:
            query = """
                SELECT ppi.id
                FROM product_pricelist_item ppi
                JOIN product_product pp
                       ON pp.id = ppi.product_id
                WHERE pp.active = TRUE
                AND ppi.active = TRUE
                AND pricelist_id = %(pricelist_id)s
                AND (
                    date_start IS NOT NULL
                    OR date_end IS NOT NULL
                );
            """
        self.flush()
        self.env.cr.execute(query, {"pricelist_id": self.id, "product_id": product_id})
        return self.env["product.pricelist.item"].browse(
            [row[0] for row in self.env.cr.fetchall()]
        )

    def _get_product_formula_items(self):
        self.ensure_one()
        query = """
            SELECT ppi.id
            FROM product_pricelist_item ppi
            JOIN product_product pp
                 ON pp.id = ppi.product_id
            WHERE ppi.pricelist_id = %(pricelist_id)s
            AND ppi.active = TRUE
            AND pp.active = TRUE
            AND ppi.applied_on = '0_product_variant'
            AND ppi.compute_price = 'formula'
            AND (
                ppi.price_surcharge IS NOT NULL
                OR ppi.price_discount IS NOT NULL
            );
        """
        self.flush()
        self.env.cr.execute(query, {"pricelist_id": self.id})
        return self.env["product.pricelist.item"].browse(
            [row[0] for row in self.env.cr.fetchall()]
        )

    def _create_cache_with_date__get_items(self):
        self.ensure_one()
        date_items = self._create_cache_with_date__get_date_items()
        product_formula_items = self._get_product_formula_items()
        child_items = date_items | product_formula_items
        overlapping_parents = self._get_overlapping_parent_items(product_formula_items)
        all_items = child_items | overlapping_parents
        all_items.filtered(lambda i: i.product_id.active)
        return all_items

    def _get_overlapping_parent_item_ids_for_product(
            self, product_ids, date_start=None, date_end=None
        ):
        """Returns overlapping parent pricelist items for a given list of product ids
        and an optional date range.
        """
        self.ensure_one()
        query = """
            WITH RECURSIVE parent_pricelist AS (
                SELECT id
                FROM product_pricelist
                WHERE id = %(pricelist_id)s
                UNION SELECT item.base_pricelist_id AS id
                      FROM product_pricelist_item item
                      INNER JOIN parent_pricelist parent
                              ON item.pricelist_id = parent.id
            )
            SELECT pi.id
            FROM product_pricelist_item pi
            JOIN parent_pricelist pp ON pi.pricelist_id = pp.id
            WHERE pi.active = TRUE
            AND pi.product_id IN %(product_ids)s
            AND date_start IS NULL or date_start <= COALESCE(%(date_end)s, 'infinity'::DATE)
            AND date_end IS NULL or date_end >= COALESCE(%(date_start)s, '-infinity'::DATE)
            AND active = TRUE;
        """
        args = {
            "product_ids": tuple(product_ids),
            "date_end": date_end,
            "date_start": date_start,
            "pricelist_id": self.id,
        }
        self.flush()
        self.env.cr.execute(query, args)
        return [row[0] for row in self.env.cr.fetchall()]

    def _get_overlapping_parent_items(self, items):
        ids = []
        for item in items:
            product_ids = tuple(
                item.product_id.ids
                if item.product_id
                else self.env["product.product"].search([]).ids
            )
            ids.extend(
                self._get_overlapping_parent_item_ids_for_product(
                    product_ids,
                    date_start=item.date_start or None,
                    date_end=item.date_end or None
                )
            )
        return self.env["product.pricelist.item"].browse(ids)

    def _create_cache_with_date__get_gap_date_for_product(self, product_id):
        """For a given product, returns a date where no date based item is active."""
        date_items = self._create_cache_with_date__get_date_items(product_id=product_id)
        if not date_items:
            return
        overlapping_groups = date_items._get_overlapping_groups(self.id)
        group_ranges = [
            group._get_date_limits(self.id, force_date=False) for group in overlapping_groups
        ]
        group_ranges.sort(
            key=lambda d: (d[0] or datetime.min, d[1] or datetime.max)
        )
        has_gaps = None
        one_day_td = timedelta(days=1)
        # TODO IFBOX
        gap_ranges = []
        for start, end in group_ranges:
            # Never starting / ending date_range. No gap.
            if not end and not start:
                return
            # If start is defined, return the day before
            elif start:
                return start - one_day_td
            # If end is defined, return the day after
            elif end:
                return end + one_day_td

    def _get_global_formula_items(self):
        self.ensure_one()
        query = """
            SELECT id
            FROM product_pricelist_item
            WHERE pricelist_id = %(pricelist_id)s
            AND active = TRUE
            AND applied_on = '3_global'
            AND compute_price = 'formula'
            AND (
                price_surcharge IS NOT NULL
                OR price_discount IS NOT NULL
            );
        """
        self.flush()
        self.env.cr.execute(query, {"pricelist_id": self.id})
        return self.env["product.pricelist.item"].browse(
            [row[0] for row in self.env.cr.fetchall()]
        )

    def _create_cache_with_date__get_values_from_item_group(self, product_id, item_list):
        """Returns raw values for a given product_id, and a recordset of
        overlapping pricelist items.
        """
        values = []
        item_model = self.env["product.pricelist.item"]
        product_items = item_model.browse([i.id for i in item_list])
        # Formula items are altering price coming from the parent.
        # It means that for each time price change on the parent,
        # the price changes on the child pricelist as well.
        # Therefore, we have to retrieve parent's overlapping items here.
        product_items |= self._get_global_formula_items()
        date_ranges = product_items._get_not_overlapping_date_ranges(self.id)
        values.extend(
            self._create_cache_with_date__get_values_from_date_ranges(
                product_id, date_ranges
            )
        )
        if not self.parent_pricelist_ids or self._is_factor_pricelist():
            # TODO not entirely True.
            # For a factor pricelist, price might change while no item based on
            # dates is active
            values.extend(self._create_cache_with_date__get_gap_values(product_id))
        return values

    def _create_cache_with_date__get_gap_values(self, product_id):
        """Returns raw values for a given product for a date where no pricelist item
        is active.

        Returns an empty list if no item based on dates is found.
        """
        # We might have some inactive product_id here.
        # Investigate why
        values = []
        if not product_id:
            return values
        at_date = self._create_cache_with_date__get_gap_date_for_product(product_id)
        if at_date:
            product_price = self._get_product_prices([product_id], at_date)
            price = product_price.get(product_id, None)
            if price is not None:
                values.append((product_id, self.id, price, None, None))
        return values

    def _create_cache_with_date__get_values_for_products(self, product_ids):
        today = date.today()
        product_prices = self._get_product_prices(product_ids, today)
        return [
            (product_id, self.id, price, None, None)
            for product_id, price in product_prices.items()
        ]

    def _create_cache_with_date__get_raw_values(self):
        values = []
        for pricelist in self:
            items = pricelist._create_cache_with_date__get_items()
            for product_id, item_list in items._group_by_product():
                values.extend(
                    pricelist._create_cache_with_date__get_values_from_item_group(
                        product_id, item_list
                    )
                )
            if pricelist._is_global_pricelist():
                # foireux missing != seen
                missing_products = self.env["product.product"].search(
                    [("id", "not in", pricelist.item_ids.product_id.ids)]
                )
                values.extend(
                    pricelist._create_cache_with_date__get_values_for_products(
                        missing_products.ids
                    )
                )
            if pricelist._is_factor_pricelist():
                missing_products = self.env["product.product"].search(
                    [("id", "not in", pricelist.item_ids.product_id.ids)]
                )
                parent_item_ids = pricelist._get_overlapping_parent_item_ids_for_product(missing_products.ids)
                parent_items = items.browse(parent_item_ids)
                for product_id, item_list in parent_items._group_by_product():
                    values.extend(
                        pricelist._create_cache_with_date__get_values_from_item_group(
                            product_id, item_list
                        )
                    )
                values.extend(
                    pricelist._create_cache_with_date__get_values_for_products(
                        missing_products.ids
                    )
                )
        return values
