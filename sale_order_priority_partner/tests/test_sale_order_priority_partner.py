# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import TransactionCase


class TestSaleOrderPriorityPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_urgent = cls.env["res.partner"].create(
            {"name": "Urgent Customer", "sale_priority": "1"}
        )
        cls.partner_normal = cls.env["res.partner"].create({"name": "Normal Customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu"}
        )

    def _new_order(self, partner, **vals):
        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 1}
                    )
                ],
                **vals,
            }
        )

    def test_partner_priority_is_default_on_order(self):
        order = self._new_order(self.partner_urgent)
        self.assertEqual(order.priority, "1")
        # ``sale_order_priority`` propagates the order priority to its lines
        self.assertEqual(order.order_line.priority, "1")

    def test_partner_without_priority_keeps_normal(self):
        order = self._new_order(self.partner_normal)
        self.assertEqual(order.priority, "0")
        self.assertEqual(order.order_line.priority, "0")

    def test_explicit_priority_is_kept_without_partner_priority(self):
        order = self._new_order(self.partner_normal, priority="1")
        self.assertEqual(order.priority, "1")
        self.assertEqual(order.order_line.priority, "1")

    def test_partner_priority_wins_over_explicit_priority(self):
        order = self._new_order(self.partner_urgent, priority="0")
        self.assertEqual(order.priority, "1")
        self.assertEqual(order.order_line.priority, "1")

    def test_order_without_line(self):
        order = self.env["sale.order"].create({"partner_id": self.partner_urgent.id})
        self.assertEqual(order.priority, "1")

    def test_priority_is_a_commercial_field(self):
        contact = self.env["res.partner"].create(
            {"name": "Contact", "parent_id": self.partner_urgent.id, "type": "contact"}
        )
        self.assertEqual(contact.sale_priority, "1")
        self.assertEqual(self._new_order(contact).priority, "1")

    def test_partner_priority_is_only_a_creation_default(self):
        order = self._new_order(self.partner_urgent)
        order.priority = "0"
        self.assertEqual(order.priority, "0")
        # changing the customer on an existing order does not reapply it
        order.partner_id = self.partner_normal
        self.assertEqual(order.priority, "0")
