# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.fields import Command

from .common import PL_PRODUCT_QTY, TU_PRODUCT_QTY, SellOnlyByPackagingCommon


class TestMinimumSellableQty(SellOnlyByPackagingCommon):
    def test_min_sellable_qty(self):
        """Check the computation of the minimum sellable quantity."""
        template = self.product.product_tmpl_id
        template.sell_only_by_packaging = False
        self.assertEqual(self.product.min_sellable_qty, 0)
        template.sell_only_by_packaging = True
        self.assertEqual(self.product.min_sellable_qty, TU_PRODUCT_QTY)
        self.assertEqual(template.min_sellable_qty, TU_PRODUCT_QTY)
        # Dropping the smallest packaging unit falls back on the bigger one
        template.uom_ids = [Command.set([self.uom_pl.id])]
        self.assertEqual(self.product.min_sellable_qty, PL_PRODUCT_QTY)
        self.assertEqual(template.min_sellable_qty, PL_PRODUCT_QTY)
        # A smaller packaging unit becomes the minimum
        uom_half_tu = self.env["uom.uom"].create(
            {
                "name": "Test half TU",
                "relative_factor": TU_PRODUCT_QTY / 2,
                "relative_uom_id": self.uom_unit.id,
            }
        )
        template.uom_ids = [Command.link(uom_half_tu.id)]
        self.assertEqual(self.product.min_sellable_qty, TU_PRODUCT_QTY / 2)
        self.assertEqual(template.min_sellable_qty, TU_PRODUCT_QTY / 2)
