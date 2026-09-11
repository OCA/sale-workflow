# Copyright 2026 Lorenzo Carta - Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests import tagged

from .common import SalePricelistMultiDiscountCommon


@tagged("post_install", "-at_install")
class TestSaleOrderLinePricelist(SalePricelistMultiDiscountCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product.list_price = 100.0

    # ------------------------------------------------------------------
    # Pricelist distribution -> SOL distribution
    # ------------------------------------------------------------------

    def test_rule_distribution_propagates_to_line(self):
        """A rule with its own distribution seeds the line with the whole list."""
        self._make_rule(distribution=[10, 5])
        order = self._make_order_on_product()
        line = order.order_line
        self.assertEqual(line.discount_distribution, [10, 5])
        self.assertAlmostEqual(line.discount, 14.5, places=4)

    def test_rule_distribution_drives_line_discount(self):
        """The rule distribution drives the aggregated line discount."""
        self._make_rule(distribution=[10, 5])
        order = self._make_order_on_product()
        line = order.order_line
        self.assertEqual(line.discount_distribution, [10, 5])
        self.assertAlmostEqual(line.discount, 14.5, places=4)

    def test_single_percent_path_unchanged(self):
        """A rule without a distribution still seeds a single percent."""
        self._make_rule(percent=20)
        order = self._make_order_on_product()
        line = order.order_line
        self.assertEqual(line.discount_distribution, [20])
        self.assertAlmostEqual(line.discount, 20.0, places=4)

    def test_subtotal_with_pricelist_distribution(self):
        """End-to-end: rule distribution affects the line subtotal."""
        self._make_rule(distribution=[10, 5])
        order = self._make_order_on_product()
        line = order.order_line
        line.tax_id = False
        # price_unit is the list_price (before any discount), subtotal applies
        # the distribution multiplicatively.
        self.assertAlmostEqual(line.price_unit, 100.0, places=2)
        self.assertAlmostEqual(line.price_subtotal, 85.5, places=2)

    def test_rule_distribution_propagates_to_invoice(self):
        """SO line seeded by a multi-discount rule -> invoice line same list."""
        self._make_rule(distribution=[10, 5, 2])
        order = self._make_order_on_product()
        self.assertEqual(order.order_line.discount_distribution, [10, 5, 2])
        order.action_confirm()
        invoice = order._create_invoices()
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda inv_line: inv_line.product_id == self.product
        )
        self.assertEqual(invoice_line.discount_distribution, [10, 5, 2])

    def test_changing_rule_distribution_reseeds_via_update_prices(self):
        """Editing the rule + 'Update Prices' converges to the new distribution."""
        rule = self._make_rule(distribution=[10, 5])
        order = self._make_order_on_product()
        line = order.order_line
        self.assertEqual(line.discount_distribution, [10, 5])
        rule.discount_distribution = [20, 10]
        order.action_update_prices()
        self.assertEqual(line.discount_distribution, [20, 10])

    def test_distribution_path_used_when_rule_has_no_percent(self):
        """A rule with distribution=[10, 5] and percent_price=0 still seeds."""
        self._make_rule(percent=0, distribution=[10, 5])
        order = self._make_order_on_product()
        line = order.order_line
        self.assertEqual(line.discount_distribution, [10, 5])
