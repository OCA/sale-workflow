# Copyright 2026 Lorenzo Carta - Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.fields import Command
from odoo.tests import tagged

from .common import SaleMultiDiscountCommon


@tagged("post_install", "-at_install")
class TestSaleOrderLine(SaleMultiDiscountCommon):
    # ------------------------------------------------------------------
    # discount_distribution / discount default behaviour
    # ------------------------------------------------------------------

    def test_default_no_discount(self):
        """A line with no manual discount has no distribution."""
        order = self._make_order()
        line = order.order_line
        self.assertFalse(line.discount_distribution)
        self.assertEqual(line.discount, 0.0)

    def test_aggregated_discount_recomputes_on_distribution_change(self):
        order = self._make_order()
        line = order.order_line
        line.discount_distribution = [10, 5]
        self.assertAlmostEqual(line.discount, 14.5, places=4)

    def test_aggregated_discount_three_values(self):
        order = self._make_order()
        line = order.order_line
        line.discount_distribution = [10, 5, 2]
        self.assertAlmostEqual(line.discount, 16.21, places=4)

    def test_aggregated_discount_clears_when_distribution_emptied(self):
        order = self._make_order()
        line = order.order_line
        line.discount_distribution = [10, 5]
        line.discount_distribution = []
        self.assertEqual(line.discount, 0.0)

    def test_aggregation_delegates_to_account_helper(self):
        """Both models must agree on the aggregation result for the same
        distribution — a regression guard against the helper drifting."""
        AML = self.env["account.move.line"]
        order = self._make_order()
        line = order.order_line
        line.discount_distribution = [10, 5, 2]
        self.assertAlmostEqual(
            line.discount,
            AML._aggregate_discount_distribution([10, 5, 2]),
            places=10,
        )

    # ------------------------------------------------------------------
    # ORM compatibility: legacy ``discount=`` writes
    # ------------------------------------------------------------------

    def test_create_with_legacy_discount_field(self):
        """Creating a line with ``discount=15`` populates the distribution."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "discount": 15,
                        }
                    )
                ],
            }
        )
        line = order.order_line
        self.assertEqual(line.discount_distribution, [15])
        self.assertAlmostEqual(line.discount, 15.0, places=4)

    def test_create_with_zero_legacy_discount(self):
        """``discount=0`` on create does not produce a stray ``[0]``."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "discount": 0,
                        }
                    )
                ],
            }
        )
        self.assertFalse(order.order_line.discount_distribution)
        self.assertEqual(order.order_line.discount, 0.0)

    def test_write_with_legacy_discount_field(self):
        """Writing only ``discount=`` overwrites the distribution."""
        order = self._make_order()
        line = order.order_line
        line.discount_distribution = [10, 5]
        line.write({"discount": 20})
        self.assertEqual(line.discount_distribution, [20])
        self.assertAlmostEqual(line.discount, 20.0, places=4)

    def test_write_with_legacy_discount_zero_clears_distribution(self):
        order = self._make_order()
        line = order.order_line
        line.discount_distribution = [10, 5]
        line.write({"discount": 0})
        self.assertFalse(line.discount_distribution)
        self.assertEqual(line.discount, 0.0)

    def test_write_with_explicit_distribution_overrides_legacy_discount(self):
        """When both ``discount`` and ``discount_distribution`` are passed,
        the distribution wins (``discount`` is ignored)."""
        order = self._make_order()
        line = order.order_line
        line.write(
            {
                "discount": 99,
                "discount_distribution": [10, 5],
            }
        )
        self.assertEqual(line.discount_distribution, [10, 5])
        self.assertAlmostEqual(line.discount, 14.5, places=4)

    # ------------------------------------------------------------------
    # Section / note lines are unaffected
    # ------------------------------------------------------------------

    def test_display_type_line_keeps_empty_distribution(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": "A section",
                            "display_type": "line_section",
                        }
                    )
                ],
            }
        )
        line = order.order_line
        self.assertFalse(line.discount_distribution)
        self.assertEqual(line.discount, 0.0)

    # ------------------------------------------------------------------
    # Order subtotal / amount integration
    # ------------------------------------------------------------------

    def test_subtotal_uses_aggregated_discount(self):
        """The line subtotal must reflect the multiplicative aggregate."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                            "tax_id": False,
                        }
                    )
                ],
            }
        )
        line = order.order_line
        line.discount_distribution = [10, 5]
        # 100 * 0.9 * 0.95 = 85.5
        self.assertAlmostEqual(line.price_subtotal, 85.5, places=2)

    # ------------------------------------------------------------------
    # SO -> Invoice propagation
    # ------------------------------------------------------------------

    def test_invoice_line_inherits_discount_distribution(self):
        """Confirming a SO and creating an invoice copies the distribution."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                            "tax_id": False,
                        }
                    )
                ],
            }
        )
        order.order_line.discount_distribution = [10, 5]
        order.action_confirm()
        invoice = order._create_invoices()
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda line: line.product_id == self.product
        )
        self.assertEqual(invoice_line.discount_distribution, [10, 5])
        self.assertAlmostEqual(invoice_line.discount, 14.5, places=4)

    # ------------------------------------------------------------------
    # Pricelist-driven discount seeding (regression: bug fix)
    # ------------------------------------------------------------------

    @classmethod
    def _pricelist_with_percentage(cls, product, percent):
        cls._enable_pricelists()
        return cls.env["product.pricelist"].create(
            {
                "name": f"Test PL {percent}%",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": product.product_tmpl_id.id,
                            "compute_price": "percentage",
                            "percent_price": percent,
                        }
                    )
                ],
            }
        )

    def test_pricelist_discount_seeds_distribution_on_product_add(self):
        """Regression: adding a product on a SO with a discounted pricelist
        must populate `discount_distribution` (and therefore `discount`)
        without needing the 'Update Prices' workaround.
        """
        pricelist = self._pricelist_with_percentage(self.product, 15)
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                        }
                    )
                ],
            }
        )
        line = order.order_line
        self.assertEqual(line.discount_distribution, [15])
        self.assertAlmostEqual(line.discount, 15.0, places=4)

    def test_create_explicit_zero_discount_overrides_pricelist(self):
        """Regression: an explicit ``discount=0`` on create must empty the
        distribution and win over the pricelist seeding.

        Mirrors the ``write`` behaviour and core's "explicit value in vals
        beats the (pre)compute". Without the ``create`` fix the popped zero
        left ``discount_distribution`` unset, letting the precompute re-seed
        it from the pricelist (here ``[15]``).
        """
        pricelist = self._pricelist_with_percentage(self.product, 15)
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "discount": 0,
                        }
                    )
                ],
            }
        )
        line = order.order_line
        self.assertFalse(line.discount_distribution)
        self.assertEqual(line.discount, 0.0)

    def test_pricelist_no_discount_keeps_empty_distribution(self):
        """A fixed-price pricelist rule must leave the distribution empty."""
        self._enable_pricelists()
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Fixed PL",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": self.product.product_tmpl_id.id,
                            "compute_price": "fixed",
                            "fixed_price": 42.0,
                        }
                    )
                ],
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                        }
                    )
                ],
            }
        )
        line = order.order_line
        self.assertFalse(line.discount_distribution)
        self.assertEqual(line.discount, 0.0)
        self.assertEqual(line.price_unit, 42.0)

    def test_pricelist_discount_recomputes_when_changing_product(self):
        """Switching the product on an existing line refreshes the distribution."""
        pricelist = self._pricelist_with_percentage(self.product, 20)
        # second product NOT in the pricelist -> distribution must be cleared
        other_product = self.env["product.product"].create(
            {
                "name": "Other",
                "list_price": 50.0,
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                        }
                    )
                ],
            }
        )
        line = order.order_line
        self.assertEqual(line.discount_distribution, [20])
        line.product_id = other_product
        self.assertFalse(line.discount_distribution)
        self.assertEqual(line.discount, 0.0)

    def test_action_update_prices_reseeds_distribution(self):
        """Changing pricelist + 'Update Prices' must converge to the new discount."""
        pl_a = self._pricelist_with_percentage(self.product, 10)
        pl_b = self._pricelist_with_percentage(self.product, 30)
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pl_a.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                        }
                    )
                ],
            }
        )
        line = order.order_line
        self.assertEqual(line.discount_distribution, [10])
        order.pricelist_id = pl_b
        order.action_update_prices()
        self.assertEqual(line.discount_distribution, [30])
        self.assertAlmostEqual(line.discount, 30.0, places=4)

    def test_pricelist_discount_propagates_to_invoice(self):
        """End-to-end: SO line seeded by pricelist -> invoice line inherits it."""
        pricelist = self._pricelist_with_percentage(self.product, 25)
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                        }
                    )
                ],
            }
        )
        self.assertEqual(order.order_line.discount_distribution, [25])
        order.action_confirm()
        invoice = order._create_invoices()
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda line: line.product_id == self.product
        )
        self.assertEqual(invoice_line.discount_distribution, [25])
        self.assertAlmostEqual(invoice_line.discount, 25.0, places=4)
