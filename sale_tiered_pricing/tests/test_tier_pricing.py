# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError

from odoo.addons.sale_tiered_pricing.tests.common import TestTieredPricing


def update_quantity(line, quantity):
    """Using a form on sale.order.line makes the product_uom_qty readonly;
       using a subform does not seem to work because the onchange is not applied,
       so save() crashes on getting the required name. So...
    """
    line.product_uom_qty = quantity
    line.product_uom_change()
    line.onchange_price_unit()


class TestPricing(TestTieredPricing):
    """We check that the prices are correctly updated, as well as the descriptions."""

    def test_tiered_pricing_constraints(self):
        def pricelist_values(items):
            return {
                "name": "Tiered pricing",
                "is_tiered_pricing": True,
                "item_ids": [(0, 0, item) for item in items],
            }

        with self.assertRaises(ValidationError):  # no tiers
            self.env["product.pricelist"].create(pricelist_values([]))

        with self.assertRaises(ValidationError):  # duplicate tiers
            items = [self.make_tier_item(0, 10), self.make_tier_item(0, 8)]
            self.env["product.pricelist"].create(pricelist_values(items))

        with self.assertRaises(ValidationError):  # negative tier
            items = [self.make_tier_item(0, 10), self.make_tier_item(-100, 8)]
            self.env["product.pricelist"].create(pricelist_values(items))

        with self.assertRaises(ValidationError):  # no starting tier
            items = [self.make_tier_item(100, 10)]
            self.env["product.pricelist"].create(pricelist_values(items))

        with self.assertRaises(ValidationError):  # a recursive tier
            bad_item = {
                "compute_price": "tier",
                "tiered_pricelist_id": self.tiered_pricing.id,
                "applied_on": "3_global",
            }
            self.env["product.pricelist"].create(pricelist_values([bad_item]))

        # check cleaning of items is done:
        abnormal_item = {
            "compute_price": "fixed",
            "fixed_price": 42,
            "applied_on": "2_product_category",
            "product_id": self.product.id,
        }
        pl = self.env["product.pricelist"].create(pricelist_values([abnormal_item]))
        message_applied = "A tier item should always be  forced to be global"
        self.assertEqual(pl.item_ids.applied_on, "3_global", message_applied)
        message_unused = "Unused fields are forced to defaults"
        self.assertEqual(bool(pl.item_ids.product_id), False, message_unused)

    def test_tiered_pricing_item_constraints(self):
        with self.assertRaises(ValidationError):  # missing a "tiered_pricelist_id"
            self.env["product.pricelist.item"].create(
                {"compute_price": "tier", "pricelist_id": self.pricelist.id}
            )

        with self.assertRaises(ValidationError):  # a recursive tier
            bad_item = {
                "compute_price": "tier",
                "pricelist_id": self.tiered_pricing.id,
                "tiered_pricelist_id": self.tiered_pricing.id,
                "applied_on": "3_global",
            }
            self.env["product.pricelist.item"].create(bad_item)

    def test_tiered_pricing(self):
        new_line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 250,
            }
        )
        self.assertEqual(new_line.price_subtotal, 100 * 10 + 100 * 8 + 50 * 7)
        self.assertTrue("Tiers" in new_line.name)
        self.assertTrue(" 10" in new_line.name)
        self.assertTrue(" 8" in new_line.name)
        self.assertTrue(" 7" in new_line.name)

        update_quantity(new_line, 150)  # because of rounding, we lose .5 on subtotal
        self.assertAlmostEqual(new_line.price_subtotal, 100 * 10 + 50 * 8, 0)
        self.assertTrue(" 10" in new_line.name)
        self.assertTrue(" 8" in new_line.name)
        self.assertTrue(" 7" not in new_line.name)

        update_quantity(new_line, 50)
        self.assertEqual(new_line.price_subtotal, 50 * 10)
        self.assertTrue(" 10" in new_line.name)
        self.assertTrue(" 8" not in new_line.name)

    def test_tiered_pricing_boundaries(self):
        """Set the tiered pricing to have tiers at 0, 1, 2 units to check boundaries.
           A tier includes its starting point and exclude its end
           (the next tier min quantity, or 'infinity').
           So they work similarly as python lists.
        """
        for i, item in enumerate(self.tiered_pricing.tier_items):
            item.min_quantity = i
        new_line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 5,
            }
        )
        self.assertEqual(len(self.tiered_pricing.tier_items), 3)
        # one item per intermediary tier, and the rest for the last one
        self.assertEqual(new_line.price_subtotal, 1 * 10 + 1 * 8 + 3 * 7)

    def test_non_tiered_pricing_items(self):
        """Check that we keep standard behaviour in other cases"""
        self.tiered_item.write({"compute_price": "fixed", "fixed_price": 42})
        new_line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 42,
            }
        )
        self.assertTrue("Tiers" not in new_line.name)
        self.assertEqual(new_line.price_subtotal, 42 * 42)
