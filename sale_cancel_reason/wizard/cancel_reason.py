# © 2013 Guewen Baconnier, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrderCancel(models.TransientModel):

    """Ask a reason for the sale order cancellation."""

    _inherit = "sale.order.cancel"

    reason_id = fields.Many2one(comodel_name="sale.order.cancel.reason", required=True)

    def action_cancel(self):
        self.ensure_one()
        res = super().action_cancel()
        self.order_id.cancel_reason_id = self.reason_id
        return res
