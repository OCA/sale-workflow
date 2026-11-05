# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form

from .common import SaleProductMultipleQtyCommon


class TestSaleProductMultipleQty(SaleProductMultipleQtyCommon):
    def test_00_round_up_compatible_uoms(self):
        """Test onchange rounds UP to a clean integer for compatible Unit UoMs.

        Pack of 5 / sales multiple Pack of 100:
        100 is divisible by 5 -> result is always a clean integer.
        - 55 packs of 5 -> 60 packs of 5 (3 x Pack of 100)

        Pack of 10 / sales multiple Pack of 100:
        100 is divisible by 10 -> result is always a clean integer.
        - 4 packs of 10 -> 10 packs of 10 (1 x Pack of 100)
        """
        with Form(self.sale) as sale_form:
            with sale_form.order_line.edit(1) as line:
                line.product_uom_qty = 55
        sale = sale_form.save()
        self.assertEqual(sale.order_line[1].product_uom_qty, 60)

        with Form(self.sale) as sale_form:
            with sale_form.order_line.edit(2) as line:
                line.product_uom_qty = 4
        sale = sale_form.save()
        self.assertEqual(sale.order_line[2].product_uom_qty, 10)

    def test_01_round_up_incompatible_uoms_ceil_to_integer(self):
        """Test onchange rounds UP to the next integer for incompatible Unit UoMs.

        Pack of 6 / sales multiple Pack of 100:
        raw step = 16.666...
        effective step = 17

        - 13 packs of 6 -> 17
        - 17 is already one valid step -> unchanged
        - 34 is already two valid steps -> unchanged
        - 35 rounds up to 50 (3 x Pack of 100 = 300 units = 50 packs of 6)
        """
        with Form(self.sale) as sale_form:
            with sale_form.order_line.edit(0) as line:
                line.product_uom_qty = 13
        sale = sale_form.save()
        self.assertEqual(sale.order_line[0].product_uom_qty, 17)

        with Form(self.sale) as sale_form:
            with sale_form.order_line.edit(0) as line:
                line.product_uom_qty = 17
        sale = sale_form.save()
        self.assertEqual(sale.order_line[0].product_uom_qty, 17)

        with Form(self.sale) as sale_form:
            with sale_form.order_line.edit(0) as line:
                line.product_uom_qty = 34
        sale = sale_form.save()
        self.assertEqual(sale.order_line[0].product_uom_qty, 34)

        with Form(self.sale) as sale_form:
            with sale_form.order_line.edit(0) as line:
                line.product_uom_qty = 35
        sale = sale_form.save()
        self.assertEqual(sale.order_line[0].product_uom_qty, 50)

    def test_02_no_rounding_when_already_multiple(self):
        """Test onchange does not modify a qty that is already a valid multiple."""
        with Form(self.sale) as sale_form:
            with sale_form.order_line.edit(1) as line:
                line.product_uom_qty = 20
        sale = sale_form.save()
        self.assertEqual(sale.order_line[1].product_uom_qty, 20)

    def test_03_no_sale_multiple_uom_no_rounding(self):
        """Test onchange does not touch qty without a Sales Multiple UoM."""
        self.product_notebook.sale_multiple_uom_id = False
        with Form(self.sale) as sale_form:
            with sale_form.order_line.edit(0) as line:
                line.product_uom_qty = 13
        sale = sale_form.save()
        self.assertEqual(sale.order_line[0].product_uom_qty, 13)

    def test_04_no_ceil_for_non_unit_reference_uoms(self):
        """Test fractional qty is preserved for non-Unit reference UoMs.

        Pack of 400g / sales multiple Pack of 1kg:
        1 kg is NOT divisible by 400g -> rounds to 2.5 packs.
        """
        # Verify UoMs do not share the Unit reference.
        self.assertFalse(self.liquid_line._sale_multiple_uom_has_unit_reference())

        # 2 x 400g -> 2.5 x 400g (fractional, must NOT be rounded up to 3)
        with Form(self.sale) as sale_form:
            with sale_form.order_line.edit(3) as line:
                line.product_uom_qty = 2
        sale = sale_form.save()
        self.assertEqual(sale.order_line[3].product_uom_qty, 2.5)

    def test_05_chained_uom_reference_rounds_to_nested_multiple(self):
        """Test chained Unit UoMs allow selecting a nested sales multiple.

        Product default UoM is Pack of 10. The sales multiple is Nested Pack of
        100, defined as 10 x Pack of 10, so ordering 4 packs must round to 10.
        """
        line = self._create_order_line(self.product_nested_box)
        self.assertEqual(line.product_uom_id, self.uom_pack_10)
        self.assertEqual(line._get_sale_multiple_step_qty(), 10)

        with Form(line.order_id) as sale_form:
            with sale_form.order_line.edit(0) as form_line:
                form_line.product_uom_qty = 4
        sale = sale_form.save()
        self.assertEqual(sale.order_line.product_uom_qty, 10)

    def test_06_box_250_rounds_to_box_500_multiple(self):
        """Test one Box of 250 rounds to two boxes for a Box of 500 multiple."""
        line = self._create_order_line(self.product_big_box)
        self.assertEqual(line.product_uom_id, self.uom_box_250)
        self.assertEqual(line._get_sale_multiple_step_qty(), 2)

        with Form(line.order_id) as sale_form:
            with sale_form.order_line.edit(0) as form_line:
                form_line.product_uom_qty = 1
        sale = sale_form.save()
        self.assertEqual(sale.order_line.product_uom_qty, 2)

    def test_07_template_sales_multiple_is_propagated_to_unique_variant(self):
        """Test template Sales Multiple writes propagate to the unique variant."""
        product = self.product_screw
        product.sale_multiple_uom_id = False
        product.product_tmpl_id.sale_multiple_uom_id = self.uom_pack_100
        self.assertEqual(product.sale_multiple_uom_id, self.uom_pack_100)
