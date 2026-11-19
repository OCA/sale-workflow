# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo import Command
from odoo.tests import TransactionCase


class TestSaleExceptionLockedLines(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, test_base_exception=True))
        cls.rule = cls.env["exception.rule"].create(
            {
                "name": "Big quantity",
                "model": "sale.order.line",
                "exception_type": "by_domain",
                "domain": "[('product_uom_qty', '>', 5)]",
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.env.ref("product.product_product_6").id,
                            "product_uom_qty": 10,
                        }
                    )
                ],
            }
        )

    def test_locked_lines_current_transaction(self):
        lines = self.order.order_line
        rule_info = self.env["exception.rule"]._get_rules_info_for_domain(
            [("id", "=", self.rule.id)]
        )[0]
        with (
            patch.object(type(lines), "_new_cursor_can_lock", return_value=False),
            patch(
                "odoo.addons.sale_exception.models.sale_order_line.Environment"
            ) as mocked_env,
        ):
            self.assertEqual(lines._detect_exceptions(rule_info), self.order)
            mocked_env.assert_not_called()
        self.assertEqual(lines.exception_ids, self.rule)
