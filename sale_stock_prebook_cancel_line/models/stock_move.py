# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _is_move_to_take_into_account_for_qty_canceled(self):
        self.ensure_one()
        return (
            not self.used_for_sale_reservation
            and super()._is_move_to_take_into_account_for_qty_canceled()
        )
