# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    blanket_reservation_strategy = fields.Selection(
        selection_add=[("at_confirm", "At Order Confirmation")],
        ondelete={"at_confirm": "cascade"},
    )

    def _get_or_create_reserve_procurement_group(self):
        """Get or create the procurement group for the reservation."""
        self.ensure_one()
        picking_reservations = self._get_reservation_pickings().filtered(
            lambda p: p.state in ("assigned", "confirmed")
        )
        if picking_reservations:
            return picking_reservations[0].group_id
        return self._create_reserve_procurement_group()

    def _blanket_order_reserve_call_off_remaining_qty(self):
        """Reserve the stock for the blanket order."""
        to_reserve, other_orders = self._split_recrodset_for_reservation_strategy(
            "at_confirm"
        )
        to_reserve._prebook_stock_for_call_off_remaining_qty()
        return super(
            SaleOrder, other_orders
        )._blanket_order_reserve_call_off_remaining_qty()

    def _blanket_order_release_call_off_remaining_qty(self):
        to_release, other_orders = self._split_recrodset_for_reservation_strategy(
            "at_confirm"
        )
        to_release._release_prebooked_stock()
        return super(
            SaleOrder, other_orders
        )._blanket_order_release_call_off_remaining_qty()

    def _prebook_stock_for_call_off_remaining_qty(self):
        """Prebook the stock for the order."""
        self.order_line._prebook_stock_for_call_off_remaining_qty()

    def _release_prebooked_stock(self):
        """Release the prebooked stock for the order."""
        self.order_line._release_reservation()
