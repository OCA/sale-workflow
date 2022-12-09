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


class TestPricelistUtilityMethods(TestPricelistCacheHistoryCommonCase):
    def assert_equals_raw_values(self, values, expected_values):
        for vals, expected_vals in zip(values, expected_values):
            list_id, prod_id, price, date_start, date_end = vals
            date_start = str(date_start.date()) if date_start else date_start
            date_end = str(date_end.date()) if date_end else date_end
            (
                expected_list_id,
                expected_prod_id,
                expected_price,
                expected_date_start,
                expected_date_end,
            ) = expected_vals
            self.assertEqual(list_id, expected_list_id)
            self.assertEqual(prod_id, expected_prod_id)
            self.assertEqual(price, expected_price)
            self.assertEqual(date_start, expected_date_start)
            self.assertEqual(date_end, expected_date_end)

    def test_create_cache_with_date__get_raw_values(self):
        list_id = self.list.id
        prod_id = self.product.id
        expected_values = [
            (prod_id, list_id, 12.0, None, "2023-01-01"),
            (prod_id, list_id, 8.0, "2023-01-02", "2023-01-06"),
            (prod_id, list_id, 8.0, "2023-01-07", "2023-01-12"),
            (prod_id, list_id, 8.0, "2023-01-13", "2023-01-17"),
            (prod_id, list_id, 8.0, "2023-01-18", "2023-01-21"),
            (prod_id, list_id, 6.0, "2023-01-22", "2023-01-22"),
            (prod_id, list_id, 6.0, "2023-01-23", None),
        ]
        values = self.list._create_cache_with_date__get_raw_values()
        self.assert_equals_raw_values(values, expected_values)

    def test_create_cache_with_date__get_raw_values_with_formula(self):
        formula_list = self.formula_list
        prod_id = self.product.id
        # While formula_list is active, it alters prices coming from the parent
        # TODO I actually expect this:
        # [
        #   (prod_id, formula_list.id, 32.0, "2023-01-01", "2023-01-01"),
        #   (prod_id, formula_list.id, 28.0, "2023-01-02", "2023-01-06"),
        #   (prod_id, formula_list.id, 28.0, "2023-01-07", "2023-01-12"),
        #   (prod_id, formula_list.id, 28.0, "2023-01-13", "2023-01-17"),
        #   (prod_id, formula_list.id, 28.0, "2023-01-18", "2023-01-21"),
        #   (prod_id, formula_list.id, 26.0, "2023-01-22", "2023-01-22"),
        #   (prod_id, formula_list.id, 26.0, "2023-01-23", "2023-01-31"),
        # ]
        # Prices before the 1st Jan are coming from the parent,
        # as well as prices after the 31th of Jan.
        # Doesn't hurt, but we'll just end up computing to much things,
        # and we might need to save time at some point.
        expected_values = [
            (prod_id, formula_list.id, 249.3376967430263, None, "2022-12-31"),
            (prod_id, formula_list.id, 32.0, "2023-01-01", "2023-01-01"),
            (prod_id, formula_list.id, 28.0, "2023-01-02", "2023-01-06"),
            (prod_id, formula_list.id, 28.0, "2023-01-07", "2023-01-12"),
            (prod_id, formula_list.id, 28.0, "2023-01-13", "2023-01-17"),
            (prod_id, formula_list.id, 28.0, "2023-01-18", "2023-01-21"),
            (prod_id, formula_list.id, 26.0, "2023-01-22", "2023-01-22"),
            (prod_id, formula_list.id, 26.0, "2023-01-23", "2023-01-31"),
            (prod_id, formula_list.id, 249.3376967430263, "2023-02-01", None),
        ]
        values = formula_list._create_cache_with_date__get_raw_values()
        self.assert_equals_raw_values(values, expected_values)
