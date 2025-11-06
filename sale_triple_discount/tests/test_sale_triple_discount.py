# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2022 Manuel Regidor - Sygel Technology
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from unittest import skip

from odoo import Command
from odoo.exceptions import ValidationError

from .common import SaleTripleDiscountCommon


class TestSaleOrder(SaleTripleDiscountCommon):
    def _test_invoice_discount(self):
        self.order.action_confirm()
        if self.order.state == "waiting_approval":  # pragma: no cover
            self.order.action_approve()
            self.assertAlmostEqual(self.order.state, "approved")
            self.order.action_confirm()
        self.order._create_invoices()
        invoice = self.order.invoice_ids[0]
        inv_line1 = invoice.invoice_line_ids.filtered(
            lambda i: i.product_id == self.product1
        )
        inv_line2 = invoice.invoice_line_ids.filtered(
            lambda i: i.product_id == self.product2
        )
        self.assertTrue(inv_line1)
        self.assertTrue(inv_line2)
        self.assertAlmostEqual(self.so_line1.discount1, inv_line1.discount1)
        self.assertAlmostEqual(self.so_line1.discount2, inv_line1.discount2)
        self.assertAlmostEqual(self.so_line1.discount3, inv_line1.discount3)
        self.assertAlmostEqual(self.so_line1.discount, inv_line1.discount)
        self.assertAlmostEqual(self.so_line1.price_subtotal, inv_line1.price_subtotal)

        self.assertAlmostEqual(self.so_line2.discount1, inv_line2.discount1)
        self.assertAlmostEqual(self.so_line2.discount2, inv_line2.discount2)
        self.assertAlmostEqual(self.so_line2.discount3, inv_line2.discount3)
        self.assertAlmostEqual(self.so_line2.discount, inv_line2.discount)
        self.assertAlmostEqual(self.so_line2.price_subtotal, inv_line2.price_subtotal)

        self.assertAlmostEqual(self.order.amount_total, invoice.amount_total)

    def test_01_sale_order_classic_discount(self) -> None:
        """Tests with single discount"""
        self.so_line1.discount1 = 50.0
        self.so_line2.discount1 = 75.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 300.0)
        self.assertAlmostEqual(self.so_line2.price_subtotal, 150.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 450.0)
        self.assertAlmostEqual(self.order.amount_tax, 67.5)
        # Mix taxed and untaxed:
        self.so_line1.tax_id = False
        self.assertAlmostEqual(self.order.amount_tax, 22.5)
        self._test_invoice_discount()

    def test_02_sale_order_simple_triple_discount(self) -> None:
        """Tests on a single line"""
        self.so_line2.unlink()
        # Divide by two on every discount:
        self.so_line1.discount1 = 50.0
        self.so_line1.discount2 = 50.0
        self.so_line1.discount3 = 50.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 75.0)
        self.order._compute_amounts()
        self.assertAlmostEqual(self.order.amount_untaxed, 75.0)
        self.assertAlmostEqual(self.order.amount_tax, 11.25)
        # Unset first discount:
        self.so_line1.discount1 = 0.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 150.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 150.0)
        self.assertAlmostEqual(self.order.amount_tax, 22.5)
        # Set a charge instead:
        self.so_line1.discount2 = -50.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 450.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 450.0)
        self.assertAlmostEqual(self.order.amount_tax, 67.5)
        # sale tax total (multiplicative)
        tax_totals = self.order.tax_totals
        self.assertAlmostEqual(tax_totals["tax_amount"], 67.5)

    @skip
    def test_03_sale_order_simple_triple_discount_2(self) -> None:  # pragma: no cover
        # FIXME: see https://github.com/OCA/sale-workflow/issues/3649
        # set discount_type to additive
        self.so_line1.discount1 = 10.0
        self.so_line1.discount2 = 10.0
        self.so_line1.discount3 = 10.0
        self.so_line1.discounting_type = "additive"
        self.assertAlmostEqual(self.so_line1.price_subtotal, 420.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 420.0)
        self.assertAlmostEqual(self.order.amount_tax, 63.0)
        # sale tax total (additive)
        tax_totals = self.order.tax_totals
        self.assertAlmostEqual(tax_totals["tax_amount"], 63.0)
        # set discount over 100%
        self.so_line1.discount1 = 30.0
        self.so_line1.discount2 = 70.0
        self.so_line1.discount3 = 50.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 0.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 0.0)
        self.assertAlmostEqual(self.order.amount_tax, 0.0)
        # set discount_type to multiplicative
        self.so_line1.discount1 = 50.0
        self.so_line1.discount2 = 50.0
        self.so_line1.discount3 = 50.0
        self.so_line1.discounting_type = "multiplicative"
        self.assertAlmostEqual(self.so_line1.price_subtotal, 75.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 75.0)
        self.assertAlmostEqual(self.order.amount_tax, 11.25)

    def test_04_sale_order_complex_triple_discount_1(self) -> None:
        """Tests on multiple lines"""
        self.so_line1.discount1 = 50.0
        self.so_line1.discount2 = 50.0
        self.so_line1.discount3 = 50.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 75.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 675.0)
        self.assertAlmostEqual(self.order.amount_tax, 101.25)
        self.so_line2.discount3 = 50.0
        self.assertAlmostEqual(self.so_line2.price_subtotal, 300.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 375.0)
        self.assertAlmostEqual(self.order.amount_tax, 56.25)
        self._test_invoice_discount()

    @skip
    def test_05_sale_order_complex_triple_discount_2(self) -> None:  # pragma: no cover
        # FIXME: see https://github.com/OCA/sale-workflow/issues/3649
        # additive discount
        self.so_line2.discounting_type = "additive"
        self.so_line1.discount1 = 50.0
        self.so_line1.discount2 = 50.0
        self.so_line1.discount3 = 50.0
        self.so_line2.discount2 = 10.0
        self.assertAlmostEqual(self.so_line2.price_subtotal, 240.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 315.0)
        self.assertAlmostEqual(self.order.amount_tax, 47.25)
        # multiplicative discount
        self.so_line2.discount2 = 0.0
        self.so_line2.discount3 = 50.0
        self.assertAlmostEqual(self.so_line2.price_subtotal, 300.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 375.0)
        self.assertAlmostEqual(self.order.amount_tax, 56.25)
        self._test_invoice_discount()

    def test_06_sale_order_complex_triple_discount_3(self) -> None:
        self.so_line2.discounting_type = "multiplicative"
        self.so_line1.discount1 = 50.0
        self.so_line1.discount2 = 50.0
        self.so_line1.discount3 = 50.0
        self.so_line2.discount2 = 10.0
        self.so_line2.discount3 = 50.0
        self.assertAlmostEqual(self.so_line2.price_subtotal, 270.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 345.0)
        self.assertAlmostEqual(self.order.amount_tax, 51.75)
        self._test_invoice_discount()

    def test_07_sale_order_triple_discount_invoicing(self) -> None:
        """When a confirmed order is invoiced, the resultant invoice
        should inherit the discounts"""
        self.so_line1.discount1 = 50.0
        self.so_line1.discount2 = 50.0
        self.so_line1.discount3 = 50.0
        self.so_line2.discount3 = 50.0
        self._test_invoice_discount()

    def test_08_round_globally(self) -> None:
        """Tests on multiple lines when 'round_globally' is active"""
        self.env.user.company_id.tax_calculation_rounding_method = "round_globally"
        self.so_line1.discount1 = 50.0
        self.so_line1.discount2 = 50.0
        self.so_line1.discount3 = 50.0
        self.assertEqual(self.so_line1.price_subtotal, 75.0)
        self.assertEqual(self.order.amount_untaxed, 675.0)
        self.assertEqual(self.order.amount_tax, 101.25)
        self.so_line2.discount3 = 50.0
        self.assertEqual(self.so_line2.price_subtotal, 300.0)
        self.assertEqual(self.order.amount_untaxed, 375.0)
        self.assertEqual(self.order.amount_tax, 56.25)
        self._test_invoice_discount()

    @skip
    def test_09_discount_0(self) -> None:  # pragma: no cover
        # FIXME: see https://github.com/OCA/sale-workflow/issues/3649
        self.so_line1.discounting_type = "additive"
        self.so_line1.discount1 = 0.0
        self.so_line1.discount2 = 0.0
        self.so_line1.discount3 = 0.0
        self.so_line2.discounting_type = "additive"
        self.so_line2.discount1 = 0.0
        self.so_line2.discount2 = 0.0
        self.so_line2.discount3 = 0.0
        self.assertAlmostEqual(self.so_line1.price_subtotal, 600.0)
        self.assertAlmostEqual(self.so_line2.price_subtotal, 600.0)
        self.assertAlmostEqual(self.order.amount_untaxed, 1200.0)
        self.assertAlmostEqual(self.order.amount_tax, 180.0)
        self._test_invoice_discount()

    def test_10_preserves_discount_precision(self) -> None:
        self.so_line1.price_unit = 1200.0
        self.so_line1.discount1 = 5.0
        self.so_line1.discount2 = 9.0
        self.so_line1.discount3 = 13.0

        discount_field = self.env["sale.order.line"]._fields["discount"]
        self.assertIsNone(discount_field._digits)
        self.assertAlmostEqual(self.so_line1.discount, 24.7885)
        self.assertAlmostEqual(self.so_line1.price_subtotal, 902.54)

    def test_11_discount_wizard(self) -> None:
        self.so_line1.discount1 = 50.0
        self.so_line1.discount2 = 50.0
        self.so_line1.discount3 = 50.0
        self.env["sale.order.discount"].create(
            {
                "sale_order_id": self.order.id,
                "discount_percentage": 0.3,
                "discount_type": "sol_discount",
            }
        ).action_apply_discount()
        self.assertAlmostEqual(self.so_line1.discount, 30)
        self.assertAlmostEqual(self.so_line1.discount1, 30)
        self.assertAlmostEqual(self.so_line1.discount2, 0)
        self.assertAlmostEqual(self.so_line1.discount3, 0)

    def test_12_discounting_type_additive_not_allowed(self) -> None:
        # FIXME: see https://github.com/OCA/sale-workflow/issues/3649
        with self.assertRaises(ValidationError):
            self.so_line1.discounting_type = "additive"

    def test_13_pricelist_discount_applies_to_discount1(self) -> None:
        """
        test that the pricelist discount is correctly applied to discount1 and standard
        discount is correctly set

        the discount is automatically recomputed when fields it depends on change,
        in this case: product_uom_qty
        """
        # create apricelist with 20% discount applicable globally from quantity >= 50
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Test Pricelist",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "3_global",
                            "compute_price": "percentage",
                            "percent_price": 20,
                            "min_quantity": 50,
                        }
                    )
                ],
            }
        )
        self.env.user.write(
            {"groups_id": [(5, self.env.ref("sale.group_discount_per_so_line").id)]}
        )
        self.order.pricelist_id = pricelist
        self.order.action_update_prices()
        # initially, with quantity below 50, no discount should apply
        self.assertAlmostEqual(self.so_line1.discount1, 0)
        self.assertAlmostEqual(self.so_line1.discount2, 0.0)
        self.assertAlmostEqual(self.so_line1.discount3, 0.0)
        self.assertAlmostEqual(self.so_line1.discount, 0.0)
        # change quantity to exceed the minimum quantity for the discount rule
        # this triggers recomputation of discount fields via the depends mechanism.
        self.so_line1.product_uom_qty = 51
        self.so_line1.discount1 = 20
        self.assertAlmostEqual(self.so_line1.discount, 20.0)
        # after changing the quantity, discount1 should be updated to 20%
        self.assertAlmostEqual(
            self.so_line1.discount1,
            20.0,
            msg="Discount1 should be set to 20% from pricelist",
        )

        self.assertAlmostEqual(self.so_line1.discount2, 0.0)
        self.assertAlmostEqual(self.so_line1.discount3, 0.0)
        self.assertAlmostEqual(self.so_line1.discount, 20.0)
        # set manually the discount and see if qty change reset discount to pricelist
        # discount
        self.so_line1.discount1 = 10
        self.so_line1.discount2 = 20
        self.so_line1.discount3 = 30
        self.assertAlmostEqual(self.so_line1.discount1, 10)
        self.assertAlmostEqual(self.so_line1.discount2, 20)
        self.assertAlmostEqual(self.so_line1.discount3, 30)
        self.assertAlmostEqual(self.so_line1.discount, 49.6)
        self.so_line1.product_uom_qty = 52
        self.so_line1.discount1 = 20
        self.assertAlmostEqual(self.so_line1.discount1, 20)
        self.assertAlmostEqual(self.so_line1.discount2, 20)
        self.assertAlmostEqual(self.so_line1.discount3, 30)
        self.assertAlmostEqual(self.so_line1.discount, 55.20)

    def test_14_explicit_zero_discount_clears_multiple_discounts(self) -> None:
        line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product1.id,
                "name": "Line with zero standard discount",
                "product_uom_qty": 1,
                "price_unit": 600,
                "discount": 0,
                "discount1": 10,
                "discount2": 20,
                "discount3": 30,
            }
        )
        self.assertEqual(line.discount1, 0)
        self.assertEqual(line.discount2, 0)
        self.assertEqual(line.discount3, 0)

    def test_15_global_discount_preserves_line_discounts(self) -> None:
        self.so_line1.discount1 = 5
        self.so_line1.discount2 = 9
        self.so_line1.discount3 = 13
        self.env["sale.order.discount"].create(
            {
                "sale_order_id": self.order.id,
                "discount_percentage": 0.1,
                "discount_type": "so_discount",
            }
        ).action_apply_discount()
        self.assertEqual(self.so_line1.discount1, 5)
        self.assertEqual(self.so_line1.discount2, 9)
        self.assertEqual(self.so_line1.discount3, 13)
