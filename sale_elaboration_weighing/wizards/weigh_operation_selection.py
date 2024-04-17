# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models


class WeightOperationSelection(models.TransientModel):
    _inherit = "weigh.operation.selection"

    @api.model
    def _get_weighing_start_screen_actions(self):
        actions = super()._get_weighing_start_screen_actions()
        actions.append(
            {
                "title": _("Elaborations"),
                "description": _("Outgoing elaborations"),
                "icon": "fa-cutlery",
                "method": "action_sale_elaboration_weighing",
            }
        )
        return actions
