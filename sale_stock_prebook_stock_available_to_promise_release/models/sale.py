# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        moves = self._get_reservation_pickings().move_lines
        if moves:
            date_priority_of_reservation = moves[0].date_priority
            self = self.with_context(
                date_priority_of_reservation=date_priority_of_reservation
            )
        return super()._action_confirm()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        date_priority_of_reservation = self.env.context.get(
            "date_priority_of_reservation"
        )
        if date_priority_of_reservation:
            values["date_priority"] = date_priority_of_reservation
        return values
