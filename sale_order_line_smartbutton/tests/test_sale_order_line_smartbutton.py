# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestSaleOrderLineSmartbutton(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls._create_product("Test product", "TEST")
        cls.product_2 = cls._create_product("Test product 2", "TEST2")

    @classmethod
    def _create_product(cls, name, code):
        return cls.env["product.product"].create(
            {
                "name": name,
                "default_code": code,
                "type": "consu",
                "list_price": 10.0,
            }
        )

    @classmethod
    def _create_sale_order(cls, lines_spec):
        return cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": line_spec[0].id,
                            "product_uom_qty": line_spec[1],
                        }
                    )
                    for line_spec in lines_spec
                ]
                + [Command.create({"display_type": "line_section", "name": "Section"})],
            }
        )

    def test_order_line_count(self):
        order = self._create_sale_order([(self.product, 1), (self.product_2, 2)])
        # The section line must not be counted.
        self.assertEqual(order.order_line_count, 2)

    def test_action_view_order_lines_domain_and_context(self):
        order = self._create_sale_order([(self.product, 1)])
        action = order.action_view_order_lines()
        expected_domain = str(
            ["&", ("display_type", "=", False), ("order_id", "=", order.id)]
        )
        self.assertEqual(str(action["domain"]), expected_domain)
        self.assertEqual(action["context"]["default_order_id"], order.id)

    def test_order_locked_related_field(self):
        order = self._create_sale_order([(self.product, 1)])
        line = order.order_line.filtered(lambda line: not line.display_type)[0]
        self.assertFalse(line.order_locked)
        order.action_confirm()
        order.action_lock()
        self.assertTrue(line.order_locked)
        # The core `write` override on sale.order.line still protects
        # locked orders regardless of our view's readonly attributes.
        with self.assertRaises(UserError):
            line.write({"price_unit": 999.0})
