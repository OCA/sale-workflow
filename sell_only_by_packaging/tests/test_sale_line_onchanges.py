# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo.tests import Form

from odoo.addons.product_packaging_level_salable.tests.common import (
    PL_PRODUCT_QTY,
    TU_PRODUCT_QTY,
)

from .common import SellOnlyByPackagingCommon


class TestPackaging(SellOnlyByPackagingCommon):
    def test_compute_qties(self):
        with Form(self.order) as so, self.assertLogs(level=logging.WARNING) as logs:
            with so.order_line.edit(0) as line:
                line.product_packaging_id = self.packaging_tu
                line.product_packaging_qty = 31
            # catch WARNING by _onchange_product_packaging_id
            self.assertEqual(len(logs.records), 1)
            self.assertEqual(logs.records[0].levelno, logging.WARNING)
        # (20*30)+20 = 31*20 = 620
        expected_qty = TU_PRODUCT_QTY + PL_PRODUCT_QTY
        self.assertEqual(self.order_line.product_uom_qty, expected_qty)
        with Form(self.order) as so:
            with so.order_line.edit(0) as line:
                line.product_packaging_qty = 30
        # 20*30 = 600
        expected_qty = PL_PRODUCT_QTY
        self.assertEqual(self.order_line.product_uom_qty, expected_qty)
