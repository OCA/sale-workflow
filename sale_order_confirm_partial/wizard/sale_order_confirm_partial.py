# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command, api, fields, models


class SaleOrderConfirmPartial(models.TransientModel):
    _name = "sale.order.confirm.partial"
    _description = "Partial Quotation Confirmation"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        required=True,
    )
    mode = fields.Selection(
        selection=[
            ("all", "All Items"),
            ("selected", "Selected Items"),
        ],
        string="Confirmation Mode",
        default="all",
        required=True,
    )
    line_ids = fields.One2many(
        comodel_name="sale.order.confirm.partial.line",
        inverse_name="wizard_id",
        string="Lines To Confirm",
    )

    @api.onchange("mode")
    def _onchange_mode(self):
        """
        If mode has been changed to 'all' then fill
        line_ids with lines of related order.
        """
        if self.mode == "all":
            self.update(
                {
                    "line_ids": [Command.clear()]
                    + [
                        Command.create({"so_line_id": line_id})
                        for line_id in self.sale_order_id.order_line.ids
                    ]
                }
            )

    def action_confirm(self):
        """
        Update quantities, confirm selected lines and
        create unconfirmed quotation if needed.
        """
        self.ensure_one()
        self.sale_order_id.action_confirm_partial(self.line_ids)
