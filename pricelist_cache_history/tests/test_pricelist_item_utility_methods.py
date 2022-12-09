# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from .common import TestPricelistCacheHistoryCommonCase

# Items created in demo.xml
# time
#     -inf  a   b  c       d     e       +inf
#        ---------------------------------
# item1: ---------->                        12.0€
# item2:        <---------->                10.0€
# item3:    <-------------------->           8.0€
# item4:                         <--------   6.0€
# result 12  8   8    8      8     6
#        --><--><--><------><---><--------

DATE_A = "2023-01-02"
DATE_B = "2023-01-07"
DATE_C = "2023-01-12"
DATE_D = "2023-01-17"
DATE_E = "2023-01-22"


class TestPricelistItemUtilityMethods(TestPricelistCacheHistoryCommonCase):
    def assert_equals_pairs(self, pairs, expected_pairs):
        for pair, expected_pair in zip(pairs, expected_pairs):
            date_start, date_end = pair
            expected_date_start, expected_date_end = expected_pair
            date_start = str(date_start.date()) if date_start else date_start
            date_end = str(date_end.date()) if date_end else date_end
            self.assertEqual(date_start, expected_date_start)
            self.assertEqual(date_end, expected_date_end)

    def test_get_dates_by_type(self):
        expected_results = [
            (False, "start"),
            (DATE_A, "start"),
            (DATE_B, "start"),
            (DATE_C, "end"),
            (DATE_D, "end"),
            (DATE_E, "start"),
            (DATE_E, "end"),
            (False, "end"),
        ]
        results = self.items._get_dates_by_type()
        for result, expected_result in zip(results, expected_results):
            result_date, result_type = result
            expected_result_date, expected_result_type = expected_result
            # We might have False or dates here.
            result_date = str(result_date.date()) if result_date else result_date
            self.assertEqual(result_date, expected_result_date)
            self.assertEqual(result_type, expected_result_type)

    def test_get_pairs(self):
        dates_by_type = self.items._get_dates_by_type()
        pairs = self.items._get_pairs(dates_by_type)
        expected_pairs = [
            (False, "2023-01-01"),
            ("2023-01-02", "2023-01-06"),
            ("2023-01-07", "2023-01-12"),
            ("2023-01-13", "2023-01-17"),
            ("2023-01-18", "2023-01-21"),
            ("2023-01-22", "2023-01-22"),
            ("2023-01-23", False),
        ]
        self.assert_equals_pairs(pairs, expected_pairs)

    def test_overlapping_groups(self):
        # With self.items, all items are overlapping:
        # item1 overlaps with item2 and item3
        # item2 overlaps with item1 and item3
        # item3 overlaps iwth item1, item2 and item4
        # item4 overlaps with item3.
        # Therefore, we should get only one group
        groups = self.items._get_overlapping_groups()
        self.assertEqual(groups, [self.items])
        # If we remove item3 from the recordset, we should have
        # [(item1, item2), (item4)]
        items = self.item1 | self.item2 | self.item4
        groups = items._get_overlapping_groups()
        expected_groups = [self.item1 | self.item2, self.item4]
        self.assertEqual(groups, expected_groups)

    def test_not_overlapping_date_ranges(self):
        # time
        #     -inf  a   b  c       d     e       +inf
        #        ---------------------------------
        # item1: ---------->                        12.0€
        # item2:        <---------->                10.0€
        # item3:    <-------------------->           8.0€
        # item4:                         <--------   6.0€
        # expects:
        #   [(False, a), (a, b), (b, c), (c, d), (d, e), (e, e), (e, False)]
        result = self.items._get_not_overlapping_date_ranges()
        expected_result = [
            (False, "2023-01-01"),
            ("2023-01-02", "2023-01-06"),
            ("2023-01-07", "2023-01-12"),
            ("2023-01-13", "2023-01-17"),
            ("2023-01-18", "2023-01-21"),
            ("2023-01-22", "2023-01-22"),
            ("2023-01-23", False),
        ]
        self.assert_equals_pairs(result, expected_result)
        # time
        #     -inf  a   b  c       d     e       +inf
        #        ---------------------------------
        # item1: ---------->                        12.0€
        # item2:        <---------->                10.0€
        # item4:                         <--------   6.0€
        # expects [(False, b), (b, c), (c, d), (e, False)]
        items = self.item1 | self.item2 | self.item4
        result = items._get_not_overlapping_date_ranges()
        expected_result = [
            (False, "2023-01-06"),
            ("2023-01-07", "2023-01-12"),
            ("2023-01-13", "2023-01-17"),
            ("2023-01-22", False),
        ]
        self.assert_equals_pairs(result, expected_result)

    def test_not_overlapping_date_ranges_with_formula(self):
        # A formula pricelist alters prices coming from the parent.
        # therefore, each time parent price changes, we have to
        # store the altered price as well.
        # Meaning that parent dates are those of the child as well
        formula_item = self.formula_list.item_ids
        overlapping_items = formula_item._get_overlapping_parent_items()
        # TODO I actually expect this:
        # expected_result = [
        #   ("2023-01-01", "2023-01-01"),
        #   ("2023-01-02", "2023-01-06"),
        #   ("2023-01-07", "2023-01-12"),
        #   ("2023-01-13", "2023-01-17"),
        #   ("2023-01-18", "2023-01-21"),
        #   ("2023-01-22", "2023-01-22"),
        #   ("2023-01-23", "2023-01-31"),
        # ]
        # Prices before the 1st Jan are coming from the parent,
        # as well as prices after the 31th of Jan.
        # Doesn't hurt, we'll just end up computing to much things
        expected_result = [
            (False, "2022-12-31"),
            ("2023-01-01", "2023-01-01"),
            ("2023-01-02", "2023-01-06"),
            ("2023-01-07", "2023-01-12"),
            ("2023-01-13", "2023-01-17"),
            ("2023-01-18", "2023-01-21"),
            ("2023-01-22", "2023-01-22"),
            ("2023-01-23", "2023-01-31"),
            ("2023-02-01", False),
        ]
        result = overlapping_items._get_not_overlapping_date_ranges()
        self.assert_equals_pairs(result, expected_result)

    def test_get_overlapping_parent_items(self):
        formula_item = self.formula_list.item_ids
        expected_overlapping_items = self.items | formula_item
        overlapping_items = formula_item._get_overlapping_parent_items()
        self.assertEqual(overlapping_items, expected_overlapping_items)
