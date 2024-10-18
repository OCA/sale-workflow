# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form, SavepointCase


class TestSplitStrategy(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_consu_1 = cls.env["product.product"].search(
            [("type", "!=", "service")], limit=1
        )
        cls.product_consu_2 = cls.env["product.product"].search(
            [("type", "!=", "service")], offset=1, limit=1
        )
        cls.product_service_1 = cls.env["product.product"].search(
            [("type", "=", "service")], limit=1
        )
        cls.product_service_2 = cls.env["product.product"].search(
            [("type", "=", "service")], offset=1, limit=1
        )

        cls.product_type_not_service_filter = cls.env["ir.filters"].create(
            {
                "name": "Product type not service",
                "domain": "[('product_id.type', '!=', 'service')]",
                "model_id": "sale.order.line",
            }
        )
        cls.product_type_not_service_strategy = cls.env[
            "sale.order.split.strategy"
        ].create(
            {
                "name": "Product type",
                "line_filter_id": cls.product_type_not_service_filter.id,
            }
        )

    @classmethod
    def _create_order(cls):
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.env["res.partner"].search([], limit=1)
        for product in [
            cls.product_consu_1,
            cls.product_consu_2,
            cls.product_service_1,
            cls.product_service_2,
        ]:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product
                line_form.product_uom_qty = 1
        return order_form.save()

    def _set_sequences_and_sections(self, order):
        for seq, line in enumerate(order.order_line, 1):
            line.sequence = seq * 10
        # First section includes only consumable
        first_section = order.order_line.create(
            {
                "order_id": order.id,
                "display_type": "line_section",
                "name": "First line",
                "sequence": 5,
            }
        )
        # Middle section includes both consumable + service
        middle_section = order.order_line.create(
            {
                "order_id": order.id,
                "display_type": "line_section",
                "name": "Middle lines",
                "sequence": 15,
            }
        )
        # Last section includes only service
        last_section = order.order_line.create(
            {
                "order_id": order.id,
                "display_type": "line_section",
                "name": "Last line",
                "sequence": 35,
            }
        )
        order_lines = order.order_line.sorted()
        self.assertEqual(order_lines[0], first_section)
        self.assertEqual(order_lines[2], middle_section)
        self.assertEqual(order_lines[5], last_section)

    def test_split_product_type(self):
        order = self._create_order()
        order.split_strategy_id = self.product_type_not_service_strategy
        self.assertEqual(len(order.order_line), 4)
        new_order = order.action_split()
        self.assertEqual(len(order.order_line), 2)
        self.assertNotIn(self.product_consu_1, order.order_line.mapped("product_id"))
        self.assertNotIn(self.product_consu_2, order.order_line.mapped("product_id"))
        self.assertIn(self.product_service_1, order.order_line.mapped("product_id"))
        self.assertIn(self.product_service_2, order.order_line.mapped("product_id"))
        self.assertEqual(len(new_order.order_line), 2)
        self.assertIn(self.product_consu_1, new_order.order_line.mapped("product_id"))
        self.assertIn(self.product_consu_2, new_order.order_line.mapped("product_id"))
        self.assertNotIn(
            self.product_service_1, new_order.order_line.mapped("product_id")
        )
        self.assertNotIn(
            self.product_service_2, new_order.order_line.mapped("product_id")
        )

    def test_split_product_type_copy_sections(self):
        order = self._create_order()
        self._set_sequences_and_sections(order)
        order.order_line.sorted()
        self.product_type_not_service_strategy.copy_sections = True
        order.split_strategy_id = self.product_type_not_service_strategy
        new_order = order.action_split()
        # As new order includes only consu product, it must include first + middle sections
        self.assertEqual(len(new_order.order_line), 4)
        self.assertIn("First line", new_order.order_line.mapped("name"))
        self.assertIn("Middle lines", new_order.order_line.mapped("name"))
        self.assertNotIn("Last line", new_order.order_line.mapped("name"))
        # As new order includes only service product, it must include middle + last sections
        self.assertEqual(len(order.order_line), 4)
        self.assertNotIn("First line", order.order_line.mapped("name"))
        self.assertIn("Middle lines", order.order_line.mapped("name"))
        self.assertIn("Last line", order.order_line.mapped("name"))

    def test_split_product_type_not_copy_sections(self):
        order = self._create_order()
        self._set_sequences_and_sections(order)
        self.assertFalse(self.product_type_not_service_strategy.copy_sections)
        order.split_strategy_id = self.product_type_not_service_strategy
        new_order = order.action_split()
        # New order does not have any section
        self.assertEqual(len(new_order.order_line), 2)
        self.assertNotIn("line_section", new_order.order_line.mapped("display_type"))
        # Old order keeps all the sections
        self.assertEqual(len(order.order_line), 5)
        self.assertIn("First line", order.order_line.mapped("name"))
        self.assertIn("Middle lines", order.order_line.mapped("name"))
        self.assertIn("Last line", order.order_line.mapped("name"))

    def test_split_product_type_not_copy_sections_remove_empty(self):
        order = self._create_order()
        self._set_sequences_and_sections(order)
        # Add extra empty section at the end
        order.order_line.create(
            {
                "order_id": order.id,
                "display_type": "line_section",
                "name": "Empty section",
                "sequence": 999,
            }
        )
        self.assertFalse(self.product_type_not_service_strategy.copy_sections)
        self.product_type_not_service_strategy.remove_empty_sections_after_split = True
        order.split_strategy_id = self.product_type_not_service_strategy
        order.action_split()
        # Old order has empty sections removed
        self.assertEqual(len(order.order_line), 4)
        self.assertNotIn("First line", order.order_line.mapped("name"))
        self.assertIn("Middle lines", order.order_line.mapped("name"))
        self.assertIn("Last line", order.order_line.mapped("name"))
        self.assertNotIn("Empty section", order.order_line.mapped("name"))
