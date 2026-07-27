# © 2013 Guewen Baconnier, Camptocamp SA
# © 2022 Landoo Sistemas de Informacion SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrderCancel(models.TransientModel):
    """Ask a reason for the sale order cancellation."""

    _name = "sale.order.cancel.wizard"
    _description = "Sale Order Cancel Wizard"

    order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Order",
        required=True,
        ondelete="cascade",
    )
    reason_id = fields.Many2one(
        "sale.order.cancel.reason", string="Reason", required=True
    )

    def action_cancel(self):
        self.ensure_one()
        self.order_id.cancel_reason_id = self.reason_id
        return self.order_id.action_cancel()
