# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tools import mute_logger

from .common import SellOnlyByPackagingCommon


class TestSaleProductByPackagingOnly(SellOnlyByPackagingCommon):
    def test_default_packaging_uom(self):
        """A new line defaults to the smallest packaging unit."""
        self.product.sell_only_by_packaging = True
        line = self.env["sale.order.line"].new(
            {"order_id": self.order.id, "product_id": self.product.id}
        )
        self.assertEqual(line.product_uom_id, self.uom_tu)

    def test_error_product_unit(self):
        """The product unit itself is not an acceptable unit."""
        self.product.sell_only_by_packaging = True
        with self.assertRaises(ValidationError):
            self.order_line.write(
                {"product_uom_id": self.uom_unit.id, "product_uom_qty": 20.0}
            )

    def test_error_partial_packaging(self):
        """A fraction of a packaging unit is not an acceptable quantity."""
        self.product.sell_only_by_packaging = True
        with self.assertRaises(ValidationError):
            self.order_line.write(
                {"product_uom_id": self.uom_tu.id, "product_uom_qty": 0.6}
            )

    def test_sale_by_packaging(self):
        """A whole number of packaging units is accepted."""
        self.product.sell_only_by_packaging = True
        self.order_line.write(
            {"product_uom_id": self.uom_tu.id, "product_uom_qty": 2.0}
        )
        self.assertEqual(self.order_line.product_uom_id, self.uom_tu)
        self.assertEqual(self.order_line.product_uom_qty, 2.0)

    def test_no_restriction_without_flag(self):
        """Without the flag, the product is sold as usual."""
        self.product.sell_only_by_packaging = False
        self.order_line.write(
            {"product_uom_id": self.uom_unit.id, "product_uom_qty": 3.0}
        )
        self.assertEqual(self.order_line.product_uom_qty, 3.0)

    def test_error_no_packaging_uom(self):
        """The flag cannot be set on a product without packaging unit."""
        product = self.env["product.product"].create(
            {"name": "Plain product", "type": "consu", "sale_ok": True}
        )
        with self.assertRaises(ValidationError):
            product.sell_only_by_packaging = True

    def test_error_not_sale_ok(self):
        """The flag cannot be set on a product that cannot be sold."""
        with self.assertRaises(ValidationError):
            self.product.write({"sale_ok": False, "sell_only_by_packaging": True})

    @mute_logger("odoo.tests.form.onchange", "odoo.tests.common.onchange")
    def test_convert_packaging_qty(self):
        """Check _convert_packaging_qty rounds up to whole packaging units."""
        self.product.sell_only_by_packaging = True
        # The quantity is left untouched while the unit does not force it
        self.assertEqual(
            self.product._convert_packaging_qty(0.6, self.uom_tu),
            0.6,
        )
        self.uom_tu.force_sale_qty = True
        for qty, expected in [(2.6, 3), (2, 2), (1.9, 2), (0.1, 1), (10.49, 11)]:
            self.assertAlmostEqual(
                self.product._convert_packaging_qty(qty, self.uom_tu),
                expected,
            )
        # The product unit is not a packaging unit, so it is never forced
        self.uom_unit.force_sale_qty = True
        self.assertEqual(
            self.product._convert_packaging_qty(2.6, self.uom_unit),
            2.6,
        )

    @mute_logger("odoo.tests.form.onchange")
    def test_form_forces_whole_packaging(self):
        """The onchange rounds the quantity up on the form view."""
        self.product.sell_only_by_packaging = True
        self.uom_tu.force_sale_qty = True
        with Form(self.order) as order_form:
            with order_form.order_line.edit(0) as line_form:
                line_form.product_uom_id = self.uom_tu
                line_form.product_uom_qty = 2.6
        self.assertEqual(self.order_line.product_uom_qty, 3)
