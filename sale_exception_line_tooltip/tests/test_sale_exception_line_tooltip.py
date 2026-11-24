# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestSaleExceptionLineTooltipCommon


class TestSaleExceptionLineTooltip(TestSaleExceptionLineTooltipCommon):
    def test_no_exception_no_tooltip(self):
        line = self._make_sale_line()
        self.assertFalse(line.exception_ids)
        self.assertFalse(line.is_exception_danger)
        self.assertFalse(line.exceptions_tooltip)

    def test_exception_triggers_tooltip(self):
        line = self._make_sale_line()
        order = line.order_id
        self.exception_rule.active = True
        self.product.sale_line_warn_msg = "tooltip"
        order.detect_exceptions()
        self.assertIn(self.exception_rule, line.exception_ids)
        self.assertTrue(line.is_exception_danger)
        self.assertEqual(line.exceptions_tooltip, self.exception_rule.name)

    def test_exception_removed_clears_tooltip(self):
        line = self._make_sale_line()
        order = line.order_id
        self.exception_rule.active = True
        self.product.sale_line_warn_msg = "tooltip"
        order.detect_exceptions()
        self.assertTrue(line.is_exception_danger)
        self.assertTrue(line.exceptions_tooltip)
        self.product.sale_line_warn_msg = False
        order.detect_exceptions()
        self.assertNotIn(self.exception_rule, line.exception_ids)
        self.assertFalse(line.is_exception_danger)
        self.assertFalse(line.exceptions_tooltip)

    def test_tooltip_lists_multiple_rules(self):
        line = self._make_sale_line()
        order = line.order_id
        other_rule = self.env["exception.rule"].create(
            {
                "name": "Other tooltip",
                "description": "Another exception on the line",
                "sequence": 41,
                "model": "sale.order.line",
                "code": "failed=True",
                "active": True,
            }
        )
        self.exception_rule.active = True
        self.product.sale_line_warn_msg = "tooltip"
        order.detect_exceptions()
        self.assertEqual(
            set(line.exceptions_tooltip.split("\n")),
            {self.exception_rule.name, other_rule.name},
        )

    def test_tooltip_uses_current_user_language(self):
        line = self._make_sale_line()
        order = line.order_id
        self.env["res.lang"]._activate_lang("fr_FR")
        self.exception_rule.active = True
        self.exception_rule.with_context(lang="fr_FR").name = "Avertissement produit"
        self.product.sale_line_warn_msg = "tooltip"
        order.detect_exceptions()
        self.assertEqual(
            line.with_context(lang="fr_FR").exceptions_tooltip,
            "Avertissement produit",
        )
        self.assertEqual(
            line.with_context(lang="en_US").exceptions_tooltip,
            "Product warning",
        )
