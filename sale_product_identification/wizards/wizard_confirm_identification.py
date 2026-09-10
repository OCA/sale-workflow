# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ConfirmIdentification(models.TransientModel):
    _name = "confirm.identification"
    _description = "Confirm Identification Wizard"

    order_ids = fields.Many2many("sale.order", string="Orders")
    message = fields.Text()

    def confirm_identification(self):
        ctx = dict(self.env.context, not_verify_optional_identification=True)
        self.order_ids.with_context(**ctx).action_confirm()
