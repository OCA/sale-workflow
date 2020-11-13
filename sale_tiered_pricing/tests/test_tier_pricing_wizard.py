# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import Warning as OdooWarning

from odoo.addons.sale_tiered_pricing.tests.common import TestTieredPricing

WIZARD_MODEL = "product.tiered_pricing.wizard"


class TestPricingWizard(TestTieredPricing):
    """We check that the prices are correctly updated, as well as the descriptions.
       Some testing the onchange for when the user selects a subset of variants...
    """

    def test_template_context(self):
        """In template context, it creates a new pricelist item for the template."""
        self.pricelist.item_ids = False
        template_id = self.product.product_tmpl_id.id
        template_context = {
            "active_model": "product.template",
            "active_ids": [template_id],
        }
        model_in_context = self.env[WIZARD_MODEL].with_context(**template_context)
        wizard = model_in_context.create({})
        wizard.pricelist_ids = self.pricelist
        wizard.create_pricelist_items()

        item = self.pricelist.item_ids[0]
        self.assertEqual(item.applied_on, "1_product")
        self.assertEqual(item.product_tmpl_id.id, template_id)

        self.assertEqual(
            self.product.product_tmpl_id.tiered_pricing_items,
            item.mapped("tiered_pricelist_id.tier_items"),
        )

    def test_variant_context(self):
        """In variant context, it creates a new pricelist item for the variant."""
        self.pricelist.item_ids = False
        product_id = self.product.id
        variant_context = {
            "active_model": "product.product",
            "active_ids": [product_id],
        }
        model_in_context = self.env[WIZARD_MODEL].with_context(**variant_context)
        wizard = model_in_context.create({})
        wizard.onchange_product_template_id()
        wizard.pricelist_ids = self.pricelist
        wizard.create_pricelist_items()

        item = self.pricelist.item_ids[0]
        self.assertEqual(item.applied_on, "0_product_variant")
        self.assertEqual(item.product_id.id, product_id)

        self.assertEqual(
            self.product.tiered_pricing_items,
            item.mapped("tiered_pricelist_id.tier_items"),
        )

    def test_constraints(self):
        wizard = self.env[WIZARD_MODEL].create({})  # all defaults!

        with self.assertRaises(OdooWarning):  # missing pricelist_ids
            wizard.create_pricelist_items()

        wizard.pricelist_ids = self.pricelist
        wizard.product_template_id = False
        with self.assertRaises(OdooWarning):  # missing template
            wizard.create_pricelist_items()

        wizard.only_variants = True
        wizard.variant_ids = False
        with self.assertRaises(OdooWarning):  # missing variant
            wizard.create_pricelist_items()
