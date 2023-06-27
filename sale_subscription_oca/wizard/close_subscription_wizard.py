# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class CloseSubscriptionWizard(models.TransientModel):
    _name = "close.reason.wizard"
    _description = "Close reason wizard"

    close_reason_id = fields.Many2one(
        comodel_name="sale.subscription.close.reason", string="Reason"
    )

    def button_confirm(self):
        sale_subscription_id = self.env["sale.subscription"].search(
            [("id", "=", self.env.context["active_id"])]
        )
        sale_subscription_id.close_reason_id = self.close_reason_id.id
        stage = sale_subscription_id.stage_id
        closed_stage = self.env["sale.subscription.stage"].search(
            [("type", "=", "post")], limit=1
        )
        if stage != closed_stage:
            sale_subscription_id.stage_id = closed_stage
            sale_subscription_id.active = False
