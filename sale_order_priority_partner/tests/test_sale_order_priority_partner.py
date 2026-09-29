# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import Form, TransactionCase


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

    def test_explicit_priority_wins_over_partner_priority(self):
        order = self._new_order(self.partner_urgent, priority="0")
        self.assertEqual(order.priority, "0")
        self.assertEqual(order.order_line.priority, "0")

    def test_order_without_line(self):
        order = self.env["sale.order"].create({"partner_id": self.partner_urgent.id})
        self.assertEqual(order.priority, "1")

    def test_partner_priority_from_default_partner_in_context(self):
        order = (
            self.env["sale.order"]
            .with_context(default_partner_id=self.partner_urgent.id)
            .create({"partner_id": self.partner_urgent.id})
        )
        self.assertEqual(order.priority, "1")

    def test_priority_is_a_commercial_field(self):
        contact = self.env["res.partner"].create(
            {"name": "Contact", "parent_id": self.partner_urgent.id, "type": "contact"}
        )
        self.assertEqual(contact.sale_priority, "1")
        self.assertEqual(self._new_order(contact).priority, "1")

    def test_priority_falls_back_on_commercial_partner(self):
        contact = self.env["res.partner"].create(
            {"name": "Contact", "parent_id": self.partner_normal.id, "type": "contact"}
        )
        # only the commercial entity carries the priority
        self.partner_normal.sale_priority = "1"
        contact.write({"sale_priority": False})
        self.assertEqual(contact.commercial_partner_id, self.partner_normal)
        self.assertEqual(self._new_order(contact).priority, "1")

    def test_partner_priority_is_only_a_creation_default(self):
        order = self._new_order(self.partner_urgent)
        order.priority = "0"
        self.assertEqual(order.priority, "0")
        # writing the customer on an existing order does not reapply it
        order.partner_id = self.partner_normal
        self.assertEqual(order.priority, "0")

    def test_onchange_partner_sets_priority(self):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner_urgent
        self.assertEqual(order_form.priority, "1")
        order = order_form.save()
        self.assertEqual(order.priority, "1")

    def test_onchange_partner_on_existing_order_updates_lines(self):
        order = self._new_order(self.partner_normal)
        self.assertEqual(order.priority, "0")
        with Form(order) as order_form:
            order_form.partner_id = self.partner_urgent
        self.assertEqual(order.priority, "1")
        self.assertEqual(order.order_line.priority, "1")

    def test_onchange_partner_without_priority_keeps_current_value(self):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner_urgent
        self.assertEqual(order_form.priority, "1")
        # a customer without priority does not reset an already chosen one
        order_form.partner_id = self.partner_normal
        self.assertEqual(order_form.priority, "1")
