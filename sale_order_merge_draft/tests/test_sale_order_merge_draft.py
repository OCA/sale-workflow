# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, new_test_user, tagged, users


@tagged("post_install", "-at_install")
class TestSaleOrderMerge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.salesman = new_test_user(
            cls.env,
            login="test_salesman",
            groups="sales_team.group_sale_salesman",
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.other_partner = cls.env["res.partner"].create({"name": "Other Customer"})
        cls.desk, cls.lamp = cls.env["product.product"].create(
            [
                {"name": "Office Desk", "list_price": 100.0},
                {"name": "Desk Lamp", "list_price": 2.0},
            ]
        )
        cls.order = cls._create_order(cls.partner, cls.desk, "2026-01-05 08:00:00")
        cls.later_order = cls._create_order(
            cls.partner, cls.lamp, "2026-02-05 08:00:00"
        )

    @classmethod
    def _create_order(cls, partner, product, date_order, qty=1.0):
        return cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "date_order": date_order,
                # group_sale_salesman only sees its own orders
                "user_id": cls.salesman.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "price_unit": product.list_price,
                        },
                    )
                ],
            }
        )

    def _merge(self, orders):
        """Merge `orders` as the salesman set up in setUpClass."""
        return orders.with_user(self.env.user).action_merge()

    @users("test_salesman")
    def test_merge_moves_lines_into_oldest_order(self):
        self._merge(self.order | self.later_order)
        self.assertEqual(self.order.order_line.product_id, self.desk | self.lamp)
        self.assertFalse(self.later_order.order_line)
        self.assertEqual(self.later_order.state, "cancel")
        self.assertEqual(self.order.state, "draft")

    @users("test_salesman")
    def test_merge_consolidates_identical_lines(self):
        twin_order = self._create_order(
            self.partner, self.desk, "2026-03-05 08:00:00", qty=3.0
        )
        self._merge(self.order | twin_order)
        self.assertEqual(len(self.order.order_line), 1)
        self.assertEqual(self.order.order_line.product_uom_qty, 4.0)

    @users("test_salesman")
    def test_merge_appends_moved_lines_after_existing_ones(self):
        self._merge(self.order | self.later_order)
        lines = self.order.order_line.sorted("sequence")
        self.assertEqual(lines.product_id, self.desk | self.lamp)
        self.assertLess(lines[0].sequence, lines[1].sequence)

    @users("test_salesman")
    def test_merge_concatenates_customer_references(self):
        self.order.client_order_ref = "REF-1"
        self.later_order.client_order_ref = "REF-2"
        self._merge(self.order | self.later_order)
        self.assertEqual(self.order.client_order_ref, "REF-1, REF-2")

    @users("test_salesman")
    def test_merge_cross_references_orders_in_the_chatter(self):
        self._merge(self.order | self.later_order)
        self.assertTrue(
            any(self.later_order.name in m.body for m in self.order.message_ids)
        )
        self.assertTrue(
            any(self.order.name in m.body for m in self.later_order.message_ids)
        )

    @users("test_salesman")
    def test_merge_keeps_sections_above_their_lines(self):
        section = self.env["sale.order.line"].create(
            {
                "order_id": self.later_order.id,
                "name": "Accessories",
                "display_type": "line_section",
                "sequence": 5,
            }
        )
        self._merge(self.order | self.later_order)
        lines = self.order.order_line.sorted("sequence")
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0].product_id, self.desk)
        self.assertEqual(lines[1], section)
        self.assertEqual(lines[2].product_id, self.lamp)
        self.assertEqual(lines[2].parent_id, section)

    @users("test_salesman")
    def test_merge_single_order_raises(self):
        with self.assertRaisesRegex(UserError, "at least two quotations"):
            self._merge(self.order)

    @users("test_salesman")
    def test_merge_confirmed_order_is_ignored(self):
        self.later_order.action_confirm()
        with self.assertRaisesRegex(UserError, "at least two quotations"):
            self._merge(self.order | self.later_order)

    @users("test_salesman")
    def test_merge_different_partner_raises(self):
        other_order = self._create_order(
            self.other_partner, self.lamp, "2026-02-05 08:00:00"
        )
        with self.assertRaisesRegex(UserError, "None of the selected quotations"):
            self._merge(self.order | other_order)

    @users("test_salesman")
    def test_merge_groups_orders_by_merge_key(self):
        other_order = self._create_order(
            self.other_partner, self.desk, "2026-01-06 08:00:00"
        )
        other_later_order = self._create_order(
            self.other_partner, self.lamp, "2026-02-06 08:00:00"
        )
        self._merge(self.order | self.later_order | other_order | other_later_order)
        self.assertEqual(len(self.order.order_line), 2)
        self.assertEqual(len(other_order.order_line), 2)
        self.assertEqual(self.later_order.state, "cancel")
        self.assertEqual(other_later_order.state, "cancel")
