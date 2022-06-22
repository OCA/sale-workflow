# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_is_zero


class StockMove(models.Model):

    _inherit = "stock.move"

    can_be_amended = fields.Boolean(
        compute="_compute_can_be_amended",
    )

    @api.depends("state", "move_line_ids.qty_done")
    def _compute_can_be_amended(self):
        """
        Look into operations in progress
        As there is one operation in progress, move cannot be modified
        as it will recompute all operations. User should start from
        the beginning, that's unwanted
        :return:
        """
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        move_can_be_amended = self.filtered(
            lambda m: m.state
            in ("waiting", "confirmed", "partially_available", "assigned")
            and all(
                float_is_zero(op.qty_done, precision_digits=precision)
                for op in m.move_line_ids
            )
        )
        move_can_be_amended.update({"can_be_amended": True})
        (self - move_can_be_amended).update({"can_be_amended": False})
