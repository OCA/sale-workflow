# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _check_moves_to_cancel(self, moves):
        self.ensure_one()
        if self.move_ids.filtered("used_for_sale_reservation"):
            raise UserError(
                _(
                    "You cannot cancel a line with prebooked moves. "
                    "Please cancel the related prebooked moves first."
                )
            )
