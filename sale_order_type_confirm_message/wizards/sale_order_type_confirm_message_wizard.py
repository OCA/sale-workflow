# Copyright 2021 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderTypeConfirmWizard(models.TransientModel):
    _name = "sale.order.type.confirm.wizard"
    _description = "Sale Order Type Confirm Message Wizard"

    order_id = fields.Many2one(
        string="Order",
        comodel_name="sale.order",
        default=lambda wizard: wizard.env.context.get("active_id"),
    )
    message = fields.Text(
        string="Message", related="order_id.type_id.confirmation_message"
    )

    def action_confirm(self):
        if self.order_id:
            return self.order_id.with_context(
                bypass_double_confirmation=True
            ).action_confirm()
