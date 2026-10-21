from unittest.mock import patch

from odoo import Command

from .common import SaleOrderGeneralDiscountTripleCommon


class TestModule(SaleOrderGeneralDiscountTripleCommon):
    def test_01_applies_general_and_pricelist_discounts(self) -> None:
        sale_order = self._create_order()
        line = sale_order.order_line
        self.assertEqual(line.discount1, 20)
        self.assertEqual(line.discount2, 10)
        self.assertEqual(line.discount3, 0)

    def test_02_applies_discounts_to_configured_positions(self) -> None:
        self._set_discount_positions("discount3", "discount2")
        sale_order = self._create_order()
        line = sale_order.order_line
        self.assertEqual(line.discount1, 0)
        self.assertEqual(line.discount2, 20)
        self.assertEqual(line.discount3, 10)

    def test_03_applies_general_discount_respecting_product_bypass(self) -> None:
        self._set_discount_positions("discount1", "discount3")
        sale_order = self._create_order()
        self.assertEqual(sale_order.order_line.discount1, 10)
        self.assertEqual(sale_order.order_line.discount3, 20)
        self.product.bypass_general_discount = True
        bypassed_order = self._create_order()
        self.assertEqual(bypassed_order.order_line.discount1, 0)
        self.assertEqual(bypassed_order.order_line.discount2, 0)
        self.assertEqual(bypassed_order.order_line.discount3, 20)
        self._set_discount_positions("discount2", "discount1")
        bypassed_order = self._create_order()
        self.assertEqual(bypassed_order.order_line.discount1, 20)
        self.assertEqual(bypassed_order.order_line.discount2, 0)
        self.assertEqual(bypassed_order.order_line.discount3, 0)
        self._set_discount_positions("discount3", "discount1")
        bypassed_order = self._create_order()
        self.assertEqual(bypassed_order.order_line.discount1, 20)
        self.assertEqual(bypassed_order.order_line.discount2, 0)
        self.assertEqual(bypassed_order.order_line.discount3, 0)

    def test_04_clears_discounts_when_positions_are_disabled(self) -> None:
        self._set_discount_positions("no_apply", "no_apply")
        sale_order = self._create_order()
        line = sale_order.order_line
        line.write({"discount1": 5, "discount2": 6, "discount3": 7})
        line._compute_discount1()
        line._compute_discount2()
        line._compute_discount3()
        self.assertEqual(line.discount1, 0)
        self.assertEqual(line.discount2, 0)
        self.assertEqual(line.discount3, 0)
        self.assertEqual(self.env["sale.order.line"]._get_pricelist_discount(), 0)

    def test_05_applies_general_discount_on_change(self) -> None:
        self._set_discount_positions("discount3", "no_apply")
        sale_order = self._create_order()
        sale_order.general_discount = 15
        sale_order.onchange_general_discount()
        self.assertEqual(sale_order.order_line.discount3, 15)

    def test_06_does_not_apply_disabled_general_discount_on_change(self) -> None:
        self._set_discount_positions("no_apply", "no_apply")
        sale_order = self._create_order()
        line = sale_order.order_line
        line.write({"discount1": 5, "discount2": 6, "discount3": 7})
        sale_order.general_discount = 15
        sale_order.onchange_general_discount()
        self.assertEqual(line.discount1, 5)
        self.assertEqual(line.discount2, 6)
        self.assertEqual(line.discount3, 7)

    def test_07_recomputes_pricelist_discounts_when_prices_update(self) -> None:
        sale_order = self._create_order()
        self.pricelist_item.percent_price = 25
        sale_order.action_update_prices()
        line = sale_order.order_line
        self.assertEqual(line.discount1, 25)
        self.assertEqual(line.discount2, 10)

    def test_08_returns_no_pricelist_discount_without_matching_rule(self) -> None:
        product = self.env["product.product"].create(
            {"name": "Product without rule", "type": "service", "list_price": 100}
        )
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [Command.create({"product_id": product.id})],
            }
        )
        line = sale_order.order_line
        self.assertFalse(line.pricelist_item_id)
        self.assertEqual(line._get_pricelist_discount(), 0)

    def test_09_returns_no_pricelist_discount_for_zero_base_price(self) -> None:
        product = self.env["product.product"].create(
            {"name": "Free product", "type": "service", "list_price": 0}
        )
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": product.product_tmpl_id.id,
                "compute_price": "percentage",
                "percent_price": 20,
            }
        )
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [Command.create({"product_id": product.id})],
            }
        )
        self.assertEqual(sale_order.order_line._get_pricelist_discount(), 0)

    def test_10_skips_discount_updates_for_reward_lines(self) -> None:
        line = self._create_order().order_line
        line.write({"discount1": 5, "discount2": 6, "discount3": 7})
        discount_positions = (
            ("no_apply", "no_apply"),
            ("discount1", "discount2"),
            ("discount3", "discount2"),
        )
        with patch.object(type(line), "_check_is_reward_line", return_value=True):
            for general_discount, pricelist_discount in discount_positions:
                self._set_discount_positions(general_discount, pricelist_discount)
                line._compute_discount1()
                line._compute_discount2()
                line._compute_discount3()
        self.assertEqual(line.discount1, 5)
        self.assertEqual(line.discount2, 6)
        self.assertEqual(line.discount3, 7)

    def test_11_returns_no_discount_for_pricelist_surcharge(self) -> None:
        product = self.env["product.product"].create(
            {"name": "Product with surcharge", "type": "service", "list_price": 100}
        )
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": product.product_tmpl_id.id,
                "compute_price": "fixed",
                "fixed_price": 1000,
            }
        )
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [Command.create({"product_id": product.id})],
            }
        )
        line = sale_order.order_line
        self.assertTrue(line.pricelist_item_id)
        self.assertGreater(
            line._get_pricelist_price(), line._get_pricelist_price_before_discount()
        )
        self.assertEqual(line._get_pricelist_discount(), 0)

    def test_12_returns_discount_for_negative_pricelist_base_price(self) -> None:
        line = self._create_order().order_line
        with (
            patch.object(type(line), "_get_pricelist_price", return_value=-120),
            patch.object(
                type(line), "_get_pricelist_price_before_discount", return_value=-100
            ),
        ):
            self.assertEqual(line._get_pricelist_discount(), -20)
