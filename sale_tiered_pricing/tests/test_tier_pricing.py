# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


def update_quantity(line, quantity):
    """Using a form on sale.order.line makes the product_uom_qty readonly;
       using a subform does not seem to work because the onchange is not applied,
       so save() crashes on getting the required name. So...
    """
    line.product_uom_qty = quantity
    line.product_uom_change()
    line.onchange_price_unit()


class TestPricing(SavepointCase):
    """We check that the prices are correctly updated, as well as the descriptions."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "lang": "en_US"}
        )
        cls.product = cls.env["product.product"].create({"name": "Test product"})

        def make_tier_item(qty, price):
            return {
                "min_quantity": qty,
                "compute_price": "fixed",
                "fixed_price": price,
                "applied_on": "3_global",
            }

        cls.make_tier_item = lambda *args: make_tier_item(*args[1:])  # noqa

        cls.tiered_pricing = cls.env["product.pricelist"].create(
            {
                "name": "Tiered pricing",
                "is_tiered_pricing": True,
                "item_ids": [
                    (0, 0, make_tier_item(0, 10)),
                    (0, 0, make_tier_item(100, 8)),
                    (0, 0, make_tier_item(200, 7)),
                ],
            }
        )

        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Pricelist using tiered pricing", "is_tiered_pricing": False}
        )
        cls.tiered_item = cls.env["product.pricelist.item"].create(
            {
                "compute_price": "tier",
                "pricelist_id": cls.pricelist.id,
                "tiered_pricelist_id": cls.tiered_pricing.id,
                "applied_on": "3_global",
            }
        )

        cls.order = cls.env["sale.order"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
            }
        )

    def test_tiered_pricing_constraints(self):
        def pricelist_values(items):
            return {
                "name": "Tiered pricing",
                "is_tiered_pricing": True,
                "item_ids": [(0, 0, item) for item in items],
            }

        with self.assertRaises(ValidationError):
            items = [self.make_tier_item(0, 10), self.make_tier_item(0, 8)]
            self.env["product.pricelist"].create(pricelist_values(items))

        with self.assertRaises(ValidationError):
            items = [self.make_tier_item(0, 10), self.make_tier_item(-100, 8)]
            self.env["product.pricelist"].create(pricelist_values(items))

        with self.assertRaises(ValidationError):
            items = [self.make_tier_item(100, 10)]
            self.env["product.pricelist"].create(pricelist_values(items))

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

    def test_volume_pricing(self):
        self.tiered_item.compute_price = "volume"
        new_line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 250,
            }
        )
        self.assertEqual(new_line.price_subtotal, 250 * 7)

        update_quantity(new_line, 150)
        self.assertEqual(new_line.price_subtotal, 150 * 8)

        update_quantity(new_line, 50)
        self.assertEqual(new_line.price_subtotal, 50 * 10)
