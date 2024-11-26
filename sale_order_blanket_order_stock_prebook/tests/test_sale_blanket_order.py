# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .common import SaleOrderBlanketOrderCase


class TestSaleBlanketOrder(SaleOrderBlanketOrderCase):
    def test_reservation_at_confirm(self):
        # Confirm the blanket order with reservation at confirm
        self.blanket_so.action_confirm()
        self.assertEqual(self.blanket_so.state, "sale")
        self.assertEqual(
            self.blanket_so.commitment_date.date(),
            self.blanket_so.blanket_validity_start_date,
        )
        self.assertTrue(
            all(self.blanket_so.order_line.move_ids.mapped("used_for_sale_reservation"))
        )
