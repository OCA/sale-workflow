# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form

from .common import PL_PRODUCT_QTY, TU_PRODUCT_QTY, Common


class TestPackaging(Common):
    def test_compute_qties(self):
        with Form(self.order) as so:
            with so.order_line.edit(0) as line:
                line.product_packaging = self.packaging_tu
                line.product_packaging_qty = 31
        # (20*30)+20 = 31*20 = 620
        expected_qty = TU_PRODUCT_QTY + PL_PRODUCT_QTY
        self.assertEqual(self.order_line.product_uom_qty, expected_qty)
        with Form(self.order) as so:
            with so.order_line.edit(0) as line:
                line.product_packaging_qty = 30
        # 20*30 = 600
        expected_qty = PL_PRODUCT_QTY
        self.assertEqual(self.order_line.product_uom_qty, expected_qty)
        self.assertEqual(self.order_line.product_packaging, self.packaging_tu)
