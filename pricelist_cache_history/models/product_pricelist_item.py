# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import timedelta

from odoo import models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    def _get_item_values(self):
        self.ensure_one()
        return {
            "pricelist_id": self.pricelist_id.id,
            "date_to_check": self.date_start or self.date_end,
            "product_id": self.product_id.id,
            "date_start": self.date_start or None,
            "date_end": self.date_end or None,
        }

    def _get_orverlap_items(self, items):
        """Returns date overlapping items.

        Note: should return self in the result.
        """
        self.ensure_one()
        if not self.date_start and not self.date_end:
            # if no date_start and date_end on self, every item is overlapping
            return items
        # TODO can probably be simplified here, since 2 date ranges [a,b], [c,d]
        # are overlapping if a <= d AND c <= b
        if not self.date_start:
            # if no date_start on self, every item beginning or ending before the
            # end of self is overlapping
            domain = [
                "|",
                ("date_start", "=", False),
                ("date_start", "<=", self.date_end),
                "|",
                ("date_end", "=", False),
                ("date_end", "<=", self.date_end),
            ]
        elif not self.date_end:
            # if no date_end on self, every item beginning or ending before the
            # end of self is overlapping
            domain = [
                "|",
                ("date_start", "=", False),
                ("date_start", ">=", self.date_start),
                "|",
                ("date_end", "=", False),
                ("date_end", ">=", self.date_start),
            ]
        else:
            domain = [
                "|",
                ("date_start", "=", False),
                ("date_start", "<=", self.date_end),
                "|",
                ("date_end", "=", False),
                ("date_end", ">", self.date_start),
            ]
        return self.search(domain)

    def _get_not_overlapping_date_ranges(self):
        """Returns a list of not overlapping date ranges.

        returns : a list of not overlapping date ranges
                -> [(date_start, date_end)]
        """
        #        a   bc      d   e       f
        # -∞ ----+---+>      |   |       |
        #        |   <+------+--->       |
        #        <---++------+---+------->
        #        |   ||      <---+-------+------------ ∞
        # res should be:
        # [
        #   (None, a-1)
        #   (a, b-1)
        #   (b, c-1)
        #   (c, d-1)
        #   (d, e-1)
        #   (e, f-1)
        #   (f, None)
        # ]
        date_start_list = self.mapped("date_start")
        date_end_list = self.mapped("date_start")
        all_dates = [date for date in date_start_list + date_end_list if date]
        return self._get_pairs(all_dates)

    def _get_pairs(self, dates):
        """TODO docstring, comments, and stuff."""
        res = []
        date_start = None
        one_day = timedelta(days=1)
        for date in dates:
            res.append((date_start, date - one_day))
            date_start = date
        res.append((date_start, None))
        return res
