# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime, timedelta
from itertools import tee  # pairwise
from itertools import groupby

from odoo import models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    def _group_by_product(self):
        items = self.sorted(lambda item: item.product_id.id)
        return groupby(items, key=lambda item: item.product_id.id)

    def _get_date_items(self):
        return self.filtered(
            lambda i: (
                i.product_id
                and i.product_id.active
                and (i.date_start or i.date_end)
            )
        )

    def _get_product_formula_items(self):
        return self.filtered(
            lambda i: (
                i.product_id
                and i.product_id.active
                and i.compute_price == "formula"
                and (i.price_surcharge or i.price_discount)
            )
        )

    def _get_global_formula_items(self):
        return self.filtered(
            lambda i: (
                not i.product_id
                and i.compute_price == "formula"
                and (i.price_surcharge or i.price_discount)
            )
        )

    def _get_dates_by_type(self, pricelist_id, date_range):
        """Returns an ordered list of date_start, date_end within
        the provided date range.

        Dates should be overlapping.
        """
        # Because we cannot compare dates with boolean values, we will
        # have to add the False values afterwards.
        # So, declare variables here, to determine if we found any of those
        # cases in the recordset.
        range_start, range_end = date_range
        result = []
        starts_with_false = range_start == datetime.min
        ends_with_false = range_end == datetime.max
        for record in self:
            is_parent_item = not record.pricelist_id.id == pricelist_id
            # TODO ugly ifbox
            if is_parent_item:
                item_start = record.date_start or datetime.min
                item_end = record.date_end or datetime.min
                if range_start <= item_start <= range_end:
                    if record.date_start:
                        result.append((record.date_start, "start"))
                if range_start <= item_end <= range_end:
                    if record.date_end:
                        result.append((record.date_end, "end"))
            else:
                if record.date_start:
                    result.append((record.date_start, "start"))
                if record.date_end:
                    result.append((record.date_end, "end"))
        # Sort
        # TODO: find a better way
        # idea: (same_date, start) should be before (same_date, end)
        indices = {"start": 0, "end": 1}
        result.sort(key=lambda d: (d[0], indices[d[1]]))
        # If there was any item with no date_start, prepend res with False
        if starts_with_false:
            result.insert(0, (False, "start"))
        # If there was any item with no date_end, append res with False
        if ends_with_false:
            result.append((False, "end"))
        return result

    def _get_not_overlapping_date_ranges(self, pricelist_id):
        """Returns a list of not overlapping date ranges.

        returns : a list of not overlapping date ranges
                -> [(date_start, date_end)]
        """
        # time
        #        -∞      a  b   c  d   e f         g       +∞
        #        --------------------------------------------
        # item1: ------------------>
        # item2: ----------->
        # item3:         <------------->
        # item4:                <------------------>
        # item5:                         <-------------------
        # First, get all dates with their type (start or end)
        result = []
        for overlapping_group in self._get_overlapping_groups(pricelist_id):
            date_range = overlapping_group._get_date_limits(pricelist_id)
            dates_by_type = overlapping_group._get_dates_by_type(
                pricelist_id, date_range
            )
            pairs = overlapping_group._get_date_ranges(dates_by_type)
            result.extend(pairs)
        return result

    def _get_date_limits(self, pricelist_id, force_date=True):
        """Returns a tuple containing the earliest date_start and the
        latest date_end from the recordset.
        """
        child_items = self.filtered(lambda i: i.pricelist_id.id == pricelist_id)
        min_date_start = min([i.date_start or datetime.min for i in child_items])
        max_date_end = max([i.date_end or datetime.max for i in child_items])
        if not force_date:
            if min_date_start == datetime.min:
                min_date_start = False
            if max_date_end == datetime.max:
                max_date_end = False
        return min_date_start, max_date_end

    def _sort_by_date(self):
        # TODO: No idea how to sort like that in python.
        query = """
            SELECT id
            FROM product_pricelist_item
            WHERE id in %(item_ids)s
            ORDER BY date_start ASC NULLS FIRST,
                     date_end ASC NULLS LAST
        """
        self.env.cr.execute(query, {"item_ids": tuple(self.ids)})
        return self.browse([row[0] for row in self.env.cr.fetchall()])

    def _get_overlapping_groups(self, pricelist_id):
        """Returns overlapping groupped items."""
        self = self._sort_by_date()
        groups = []
        current_group = False
        current_date_end = False
        for item in self:
            if not current_group:
                current_group = item
                current_date_end = item.date_end
                continue
            if not current_date_end:
                # we have a never ending item in the group.
                # Current group is overlapping with every remaining item,
                # since the recordset is sorted by date_start.
                current_group |= item
                continue
            elif current_date_end >= (item.date_start or datetime.min):
                current_group |= item
                # If item.pricelist_id != pricelist_id, it means that this item
                # is coming from a parent pricelist.
                # It is part of the group, but shouldn't alter it by expanding its
                # range.
                if item.pricelist_id.id != pricelist_id:
                    continue
                if not item.date_end:
                    # item is a never ending item
                    current_date_end = item.date_end
                elif current_date_end < item.date_end:
                    # current_date_end is inferior to item's, replace it.
                    current_date_end = item.date_end
                continue
            # item is not overlapping with current group
            # Store the group in the list of groups, and create a new one.
            groups.append(current_group)
            current_group = item
            current_date_end = item.date_end
        if current_group:
            groups.append(current_group)
        return groups

    def _get_date_ranges(self, dates):
        """From a list of dates, return a list date ranges.
        
        [A, B, C] -> [(A, B), (B, C)]
        """

        # Copied from itertools documentation.
        # TODO To be replaced by itertools.pairwise when python >= 3.10
        def pairwise(dates):
            a, b = tee(dates)
            next(b, None)
            return zip(a, b)

        one_day = timedelta(days=1)
        result = []
        for pair in pairwise(dates):
            # If date_start is coming from item.date_end, it is exclusive,
            # and we should add a day
            date_start, date_start_type = pair[0]
            if date_start_type == "end":
                date_start += one_day
            # If date_end is coming from item.date_start, it is exclusive,
            # and we should retrieve one day
            date_end, date_end_type = pair[1]
            if date_end_type == "start":
                date_end -= one_day
            result.append((date_start, date_end))
        return result
