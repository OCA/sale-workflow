# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestTieredPricing(SavepointCase):
    """Adds a basic tiered pricing and a pricelist using it."""

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
