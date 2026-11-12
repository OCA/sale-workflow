# Copyright 2026 OBS Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common, tagged

from odoo.addons.sale_restricted_qty.models.product_restricted_qty_mixin import (
    RESTRICTION_DISABLED,
    RESTRICTION_ENABLED,
)


@tagged("post_install", "-at_install")
class TestMigrationRepair(common.TransactionCase):
    """Cover the 18.0.3.0.0 data-repair logic exposed as a model method."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Category = cls.env["product.category"]
        cls.Template = cls.env["product.template"]

    def _pin(self, record, mode):
        """Force a raw stored own restriction mode, as older data / the buggy
        inverse would have left it."""
        record.write(
            {
                "sale_own_restrict_min_qty": mode,
                "is_sale_own_restrict_min_qty_set": True,
            }
        )

    def test_repair_restrict_inheritance(self):
        # Top category: Warning with a value (the inherited baseline).
        category = self.Category.create(
            {
                "name": "Cat",
                "sale_min_qty": 10.0,
                "sale_restrict_min_qty": RESTRICTION_DISABLED,  # Warning
            }
        )

        # 1. Variant artefact: template inherits Warning, but the variant is
        #    frozen on Blocking (the reported bug).
        template_a = self.Template.create({"name": "A", "categ_id": category.id})
        variant_a = template_a.product_variant_id
        self._pin(variant_a, RESTRICTION_ENABLED)
        self.assertEqual(variant_a.sale_restrict_min_qty, RESTRICTION_ENABLED)

        # 2. Genuine template override: Blocking, differs from the category.
        template_b = self.Template.create({"name": "B", "categ_id": category.id})
        self._pin(template_b, RESTRICTION_ENABLED)

        # 3. Redundant template override: Warning, same as the category.
        template_c = self.Template.create({"name": "C", "categ_id": category.id})
        self._pin(template_c, RESTRICTION_DISABLED)

        # 4. Orphan: restriction set on a category with no quantity value.
        orphan = self.Category.create({"name": "Orphan"})
        self._pin(orphan, RESTRICTION_ENABLED)

        self.env["product.product"]._repair_restrict_inheritance()

        # 1. Variant re-inherits the template's (inherited) Warning.
        self.assertFalse(variant_a.is_sale_own_restrict_min_qty_set)
        self.assertEqual(variant_a.sale_restrict_min_qty, RESTRICTION_DISABLED)
        # 2. Genuine template override is kept.
        self.assertTrue(template_b.is_sale_own_restrict_min_qty_set)
        self.assertEqual(template_b.sale_restrict_min_qty, RESTRICTION_ENABLED)
        # 3. Redundant override dropped -> re-inherits.
        self.assertFalse(template_c.is_sale_own_restrict_min_qty_set)
        self.assertFalse(template_c.sale_own_restrict_min_qty)
        # 4. Orphan dropped.
        self.assertFalse(orphan.is_sale_own_restrict_min_qty_set)
        self.assertFalse(orphan.sale_own_restrict_min_qty)
