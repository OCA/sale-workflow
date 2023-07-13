# Copyright 2023 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.onchange("sequence")
    def _onchange_sequence(self):
        if self.sale_line_id:
            raise UserError(
                _(
                    "Not allowed to change the sequence of moves from the picking, "
                    "you can do it from the SO."
                )
            )
