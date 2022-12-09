# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import timedelta
from itertools import tee  # pairwise

from odoo import models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    # def _get_item_values(self):
    # self.ensure_one()
    # return {
    # "pricelist_id": self.pricelist_id.id,
    # "date_to_check": self.date_start or self.date_end,
    # "product_id": self.product_id.id,
    # "date_start": self.date_start or None,
    # "date_end": self.date_end or None,
    # }

    def _get_dates_by_type(self):
        """Returns an ordered list of date_start, date_end.

        Dates should be overlapping.
        """
        result = []
        # Because we cannot compare dates with boolean values, we will
        # have to add the False values afterwards.
        # So, declare variables here, to determine if we found any of those
        # cases in the recordset.
        starts_with_false = False
        ends_with_false = False
        for record in self:
            # Skip if no date start
            if record.date_start:
                result.append((record.date_start, "start"))
            else:
                starts_with_false = True
            # Skip if no date end
            if record.date_end:
                result.append((record.date_end, "end"))
            else:
                ends_with_false = True
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

    def _get_not_overlapping_date_ranges(self):
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
        overlapping_groups = self._get_overlapping_groups()
        for overlapping_group in overlapping_groups:
            dates_by_type = overlapping_group._get_dates_by_type()
            pairs = overlapping_group._get_pairs(dates_by_type)
            result.extend(pairs)
        return result

    def _sort_by_date(self):
        # TODO find better
        self.env.cr.execute(
            """
            SELECT id
            FROM product_pricelist_item
            WHERE id in %(item_ids)s
            ORDER BY date_start ASC NULLS FIRST,
                     date_end ASC NULLS LAST
            """,
            {"item_ids": tuple(self.ids)},
        )
        return self.browse([row[0] for row in self.env.cr.fetchall()])

    def _get_overlapping_groups(self):
        """Returns overlapping groupped items."""
        self = self._sort_by_date()
        groups = []
        current_group = False
        current_date_end = False
        # TODO clean that up
        for item in self:
            if not current_group:
                current_group = item
                current_date_end = item.date_end
                continue
            if not current_date_end:
                # we have a never ending item in the group.
                # every item is overlapping
                current_group |= item
                continue
            elif current_date_end >= item.date_start:
                current_group |= item
                if not item.date_end:
                    # item is a never ending item
                    current_date_end = item.date_end
                elif current_date_end < item.date_end:
                    # current_date_end is inferior to item's, replace it.
                    current_date_end = item.date_end
                continue
            # item is not overlapping with current group
            groups.append(current_group)
            current_group = item
            current_date_end = item.date_end
        if current_group:
            groups.append(current_group)
        return groups

    def _get_overlapping_parent_items(self):
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
            WHERE pi.product_id = %(product_id)s
            AND date_start IS NULL or date_start <= %(date_end)s
            AND date_end IS NULL or date_end >= %(date_start)s
            AND active = TRUE;
        """
        self.flush()
        ids = []
        for item in self:
            args = {
                "product_id": item.product_id.id,
                "date_end": item.date_end,
                "date_start": item.date_start,
                "pricelist_id": item.pricelist_id.id,
            }
            self.env.cr.execute(query, args)
            ids.extend([row[0] for row in self.env.cr.fetchall()])
        return self.browse(ids)

    def _get_pairs(self, dates):
        """TODO docstring, comments, and stuff."""

        # Copied from itertools documentation.
        # TODO To be replaced by itertools.pairwise when python >= 3.10
        def pairwise(dates):
            a, b = tee(dates)
            next(b, None)
            return zip(a, b)

        one_day = timedelta(days=1)
        result = []
        for pair in pairwise(dates):
            date_start, date_start_type = pair[0]
            if date_start_type == "end":
                date_start += one_day
            date_end, date_end_type = pair[1]
            if date_end_type == "start":
                date_end -= one_day
            result.append((date_start, date_end))
        return result
