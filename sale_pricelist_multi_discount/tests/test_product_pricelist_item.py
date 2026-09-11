# Copyright 2026 Lorenzo Carta - Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests import tagged

from .common import SalePricelistMultiDiscountCommon


@tagged("post_install", "-at_install")
class TestProductPricelistItem(SalePricelistMultiDiscountCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product.list_price = 100.0
        cls.uom = cls.product.uom_id
        cls.today = cls.env.cr.now().date()

    def _compute(self, rule):
        """Run ``_compute_price`` with the standard test parameters."""
        return rule._compute_price(
            self.product,
            1.0,
            self.uom,
            self.today,
            currency=self.pricelist.currency_id,
        )

    # ------------------------------------------------------------------
    # Field default
    # ------------------------------------------------------------------

    def test_default_distribution_is_empty(self):
        """A new rule with a zero discount has an empty distribution (the
        falsy-or-list contract is what every helper relies on)."""
        rule = self._make_rule(percent=0)
        self.assertFalse(rule.discount_distribution)
        self.assertAlmostEqual(rule.percent_price, 0.0, places=2)

    # ------------------------------------------------------------------
    # Distribution <-> native fields synchronisation
    # ------------------------------------------------------------------

    def test_percent_price_mirrors_distribution(self):
        """The distribution is aggregated multiplicatively into the native
        ``percent_price`` so core ``_compute_price`` works unchanged."""
        rule = self._make_rule(distribution=[10, 5])
        # 1 - 0.9 * 0.95 = 0.145
        self.assertAlmostEqual(rule.percent_price, 14.5, places=2)
        self.assertAlmostEqual(rule.price_discount, 14.5, places=2)

    def test_inverse_seeds_distribution_from_percent_price(self):
        """A direct write on ``percent_price`` rewrites the distribution to a
        single element, keeping both representations aligned."""
        rule = self._make_rule(percent=0)
        rule.percent_price = 25.0
        self.assertEqual(rule.discount_distribution, [25.0])
        self.assertAlmostEqual(rule.percent_price, 25.0, places=2)

    def test_inverse_clears_distribution_on_zero(self):
        rule = self._make_rule(distribution=[10, 5])
        rule.percent_price = 0.0
        self.assertFalse(rule.discount_distribution)

    # ------------------------------------------------------------------
    # Percentage mode
    # ------------------------------------------------------------------

    def test_percentage_single_value(self):
        """A single ``percent_price`` keeps the classic semantics."""
        rule = self._make_rule(percent=10)
        self.assertAlmostEqual(self._compute(rule), 90.0, places=2)

    def test_percentage_with_distribution_applies_multiplicatively(self):
        rule = self._make_rule(distribution=[10, 5])
        # 100 * 0.9 * 0.95 = 85.5
        self.assertAlmostEqual(self._compute(rule), 85.5, places=2)

    # ------------------------------------------------------------------
    # Formula mode
    # ------------------------------------------------------------------

    def test_formula_with_distribution(self):
        rule = self._make_rule(distribution=[10, 5], compute_price="formula")
        self.assertAlmostEqual(self._compute(rule), 85.5, places=2)

    def test_formula_single_value(self):
        """Formula mode with a single ``price_discount`` stays classic."""
        rule = self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "compute_price": "formula",
                "price_discount": 10.0,
            }
        )
        self.assertEqual(rule.discount_distribution, [10.0])
        self.assertAlmostEqual(self._compute(rule), 90.0, places=2)

    # ------------------------------------------------------------------
    # Fixed mode is unaffected
    # ------------------------------------------------------------------

    def test_fixed_mode_is_unaffected_by_distribution(self):
        """Distribution is ignored when ``compute_price='fixed'``."""
        rule = self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "compute_price": "fixed",
                "fixed_price": 42.0,
                "discount_distribution": [10, 5],
            }
        )
        self.assertAlmostEqual(self._compute(rule), 42.0, places=2)
