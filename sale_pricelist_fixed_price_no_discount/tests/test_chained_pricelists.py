# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestChainedPricelistDiscountProtection(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.ref("base.user_root").groups_id |= cls.env.ref(
            "sale.group_discount_per_so_line"
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Protected product",
                "list_price": 100.0,
                "taxes_id": [Command.clear()],
            }
        )
        cls.base_pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Protected fixed prices",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": cls.product.product_tmpl_id.id,
                            "compute_price": "fixed",
                            "fixed_price": 80.0,
                            "fixed_price_no_discount": True,
                        }
                    )
                ],
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "pricelist_id": cls.base_pricelist.id,
                "date_order": "2026-06-15 12:00:00",
            }
        )

    def _chain_pricelist(self, base_pricelist, **rule_values):
        values = {
            "applied_on": "3_global",
            "compute_price": "formula",
            "base": "pricelist",
            "base_pricelist_id": base_pricelist.id,
        }
        values.update(rule_values)
        return self.env["product.pricelist"].create(
            {"name": "Intermediate pricelist", "item_ids": [Command.create(values)]}
        )

    def _create_line(self, **values):
        return self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                **values,
            }
        )

    def test_multiple_formulas_preserve_price_and_block_manual_discount(self):
        intermediate = self._chain_pricelist(
            self.base_pricelist, price_discount=10.0, price_surcharge=3.0
        )
        self.order.pricelist_id = self._chain_pricelist(
            intermediate, price_discount=-20.0, price_surcharge=2.0
        )
        line = self._create_line()
        self.assertTrue(line.fixed_price_pricelist_rule)
        self.assertAlmostEqual(line.price_unit, 92.0)
        self.assertAlmostEqual(line.price_subtotal, 92.0)
        self.assertEqual(line.discount, 0.0)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            line.write({"discount": 5.0})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self._create_line(discount=5.0)

    def test_percentage_adjustment_is_included_in_unit_price(self):
        self.order.pricelist_id = self._chain_pricelist(
            self.base_pricelist, compute_price="percentage", percent_price=10.0
        )
        line = self._create_line()
        self.assertTrue(line.fixed_price_pricelist_rule)
        self.assertEqual(line.discount, 0.0)
        self.assertAlmostEqual(line.price_unit, 72.0)
        self.assertAlmostEqual(line.price_subtotal, 72.0)

    def test_formula_rounding_and_margin_are_preserved(self):
        self.order.pricelist_id = self._chain_pricelist(
            self.base_pricelist,
            price_discount=10.0,
            price_round=5.0,
            price_surcharge=3.0,
            price_min_margin=-2.0,
        )
        line = self._create_line()
        self.assertTrue(line.fixed_price_pricelist_rule)
        self.assertAlmostEqual(line.price_unit, 78.0)
        self.assertAlmostEqual(line.price_subtotal, 78.0)

    def test_unprotected_fixed_price_allows_manual_discount(self):
        self.base_pricelist.item_ids.fixed_price_no_discount = False
        self.order.pricelist_id = self._chain_pricelist(self.base_pricelist)
        line = self._create_line()
        self.assertFalse(line.fixed_price_pricelist_rule)
        line.write({"discount": 5.0})
        self.assertEqual(line.discount, 5.0)

    def test_quantity_selects_the_actual_base_rule(self):
        self.base_pricelist.item_ids.min_quantity = 10.0
        self.order.pricelist_id = self._chain_pricelist(self.base_pricelist)
        line = self._create_line()
        self.assertFalse(line.fixed_price_pricelist_rule)
        self.assertAlmostEqual(line.price_unit, 100.0)
        line.write({"product_uom_qty": 10.0})
        self.assertTrue(line.fixed_price_pricelist_rule)
        self.assertAlmostEqual(line.price_unit, 80.0)

    def test_base_rule_selection_converts_quantity_to_product_uom(self):
        self.base_pricelist.item_ids.min_quantity = 10.0
        self.order.pricelist_id = self._chain_pricelist(self.base_pricelist)
        line = self._create_line(product_uom=self.env.ref("uom.product_uom_dozen").id)
        self.assertTrue(line.fixed_price_pricelist_rule)
        self.assertAlmostEqual(line.price_unit, 960.0)

    def test_expired_base_rule_does_not_protect_price(self):
        self.base_pricelist.item_ids.date_end = "2026-06-14 23:59:59"
        self.order.pricelist_id = self._chain_pricelist(self.base_pricelist)
        line = self._create_line()
        self.assertFalse(line.fixed_price_pricelist_rule)
        self.assertAlmostEqual(line.price_unit, 100.0)

    def test_base_rule_for_another_product_does_not_protect_price(self):
        other_product = self.env["product.product"].create({"name": "Other product"})
        self.base_pricelist.item_ids.product_tmpl_id = other_product.product_tmpl_id
        self.order.pricelist_id = self._chain_pricelist(self.base_pricelist)
        line = self._create_line()
        self.assertFalse(line.fixed_price_pricelist_rule)
        self.assertAlmostEqual(line.price_unit, 100.0)

    def test_formula_based_on_sales_price_does_not_follow_unused_pricelist(self):
        self.order.pricelist_id = self._chain_pricelist(
            self.base_pricelist, base="list_price", price_discount=10.0
        )
        line = self._create_line()
        self.assertFalse(line.fixed_price_pricelist_rule)
        self.assertAlmostEqual(line.price_unit, 90.0)

    def test_fixed_rule_stops_lookup_even_with_pricelist_base(self):
        self.order.pricelist_id = self._chain_pricelist(
            self.base_pricelist,
            compute_price="fixed",
            fixed_price=60.0,
            fixed_price_no_discount=False,
        )
        line = self._create_line()
        self.assertFalse(line.fixed_price_pricelist_rule)
        self.assertAlmostEqual(line.price_unit, 60.0)
