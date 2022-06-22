# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    can_be_amended = fields.Boolean(
        compute="_compute_can_be_amended",
    )

    @api.depends("move_lines.can_be_amended")
    def _compute_can_be_amended(self):
        """
        Look if all moves in the picking can be modified
        :return:
        """
        for picking in self:
            picking.can_be_amended = all(
                move.can_be_amended
                for move in picking.move_lines.filtered(lambda m: m.state != "cancel")
            )
