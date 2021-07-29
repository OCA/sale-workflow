# Copyright 2021 Lorenzo Battistini @ TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AbstractWizard(models.AbstractModel):
    _name = "massive.confirm.sale.order.wizard"
    _description = "Massive Confirm Sale Order Wizard"

    order_ids = fields.Many2many(
        comodel_name="sale.order",
        string="Affected Orders",
        domain=lambda self: [
            ("state", "in", ["draft", "sent"]),
            ("user_id", "=", self.env.user.id),
        ],
        required=True,
    )

    def button_confirm(self):
        self.ensure_one()
        for order_id in self.order_ids:
            order_id.action_confirm()
