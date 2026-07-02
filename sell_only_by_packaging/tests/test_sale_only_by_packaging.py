# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tools import mute_logger

from .common import SellOnlyByPackagingCommon


class TestSaleProductByPackagingOnly(SellOnlyByPackagingCommon):
    def test_write_auto_fill_packaging(self):
        order_line = self.order.order_line
        if order_line.product_packaging_id:
            self.assertEqual(order_line.product_packaging_id.product_id, self.product)
            self.assertTrue(order_line.product_packaging_id.sales)

        order_line.write({"product_uom_qty": 3.0})
        self.assertFalse(order_line.product_packaging_id)
        self.assertFalse(order_line.product_packaging_qty)

        self.product.write({"sell_only_by_packaging": True})
        self.assertFalse(order_line.product_packaging_id)
        self.assertFalse(order_line.product_packaging_qty)

        order_line.write({"product_uom_qty": self.packaging_tu.qty * 2})
        self.assertTrue(order_line.product_packaging_id)
        self.assertTrue(order_line.product_packaging_qty)
        self.assertEqual(order_line.product_packaging_id, self.packaging_tu)
        self.assertEqual(order_line.product_packaging_qty, 2)

        with self.assertRaises(ValidationError):
            order_line.write({"product_packaging_id": False})

    def test_error_sale_packaging(self):
        # If qty does not match a packaging qty, an exception should be raised
        self.product.sell_only_by_packaging = True
        with self.assertRaises(ValidationError):
            with Form(self.order) as so:
                with so.order_line.new() as so_line:
                    so_line.product_id = self.product
                    so_line.product_uom_qty = 2

    @mute_logger("odoo.tests.form.onchange", "odoo.tests.common.onchange")
    def test_convert_packaging_qty(self):
        """
        Test if the function _convert_packaging_qty is correctly applied
        during SO line create/edit and if qties are corrects.
        :return:
        """
        self.product.sell_only_by_packaging = True
        packaging = self.packaging_tu
        # For this step, the qty is not forced on the packaging
        # But the warning will be raise because the value of packaging qty is
        # not integer package
        with self.assertRaises(ValidationError):
            self.order_line.write(
                {
                    "product_packaging_id": packaging,
                    "product_packaging_qty": 0.6,
                }
            )

        # Now force the qty on the packaging
        packaging.force_sale_qty = True
        for qty, expected in [
            (52, 60),
            (40, 40),
            (38, 40),
            (22, 40),
            (72, 80),
            (209.98, 220),
        ]:
            self.assertAlmostEqual(
                self.product._convert_packaging_qty(
                    qty, self.product.uom_id, packaging=packaging
                ),
                expected,
                places=self.precision,
            )

    def test_onchange_qty_is_not_pack_multiple(self):
        """Check package when qantity is not a multiple of package quantity.

        When the uom quantity is changed for a value not a multpile of a
        possible package an error is raised.
        """
        self.product.write({"sell_only_by_packaging": True})
        self.order_line.product_uom_qty = 40  # 2 packs
        with self.assertRaises(ValidationError):
            self.order_line.product_packaging_qty = 0.9
            self.assertAlmostEqual(
                self.order_line.product_uom_qty, 18, places=self.precision
            )
