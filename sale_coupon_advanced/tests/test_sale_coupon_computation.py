# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .common import TestSaleCoupon


class TestSaleCouponCumulative(TestSaleCoupon):
    def setUp(self):
        super().setUp()

    def test_all_programs_cumulative_auto_apply(self):
        # all programs applied
        order = self._create_order()
        programs = order._get_applicable_no_code_promo_program()
        expected_result = self.program_a + self.program_b + self.program_c
        self.assertEqual(programs, expected_result)

    def test_non_cumulative_programs_auto_apply(self):
        # programs is cutted to first cumulative
        self.program_b.is_cumulative = True
        order = self._create_order()
        programs = order._get_applicable_no_code_promo_program()
        expected_result = self.program_a + self.program_b
        self.assertEqual(programs, expected_result)
