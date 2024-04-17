# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.osv import expression


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def action_sale_elaboration_weighing(self):
        """Used in the start screen"""
        action = self.action_outgoing_weighing_operations()
        action["name"] = _("Weigh elaborations")
        action["domain"] = expression.AND(
            [
                action["domain"],
                ["|", ("elaboration_note", "!=", ""), ("elaboration_ids", "!=", False)],
            ]
        )
        return action
