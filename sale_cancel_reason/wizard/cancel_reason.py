# © 2013 Guewen Baconnier, Camptocamp SA
# © 2022 Landoo Sistemas de Informacion SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrderCancel(models.TransientModel):

    """Ask a reason for the sale order cancellation."""

    _inherit = "sale.order.cancel"

    reason_id = fields.Many2one(
        "sale.order.cancel.reason", string="Reason", required=True
    )

    def action_cancel(self):
        self.order_id.cancel_reason_id = self.reason_id
        return super(SaleOrderCancel, self).action_cancel()
