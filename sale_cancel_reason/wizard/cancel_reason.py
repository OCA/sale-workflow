# © 2013 Guewen Baconnier, Camptocamp SA
# © 2022 Landoo Sistemas de Informacion SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleOrderCancel(models.TransientModel):
    """Ask a reason for the sale order cancellation."""

    _name = "sale.order.cancel"
    _description = "Sales Order Cancel"

    order_id = fields.Many2one(
        "sale.order", string="Sale Order", required=True, ondelete="cascade"
    )
    reason_id = fields.Many2one(
        "sale.order.cancel.reason", string="Reason", required=True
    )
    display_invoice_alert = fields.Boolean(
        "Invoice Alert", compute="_compute_display_invoice_alert"
    )

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        if not values.get("order_id"):
            order_id = self.env.context.get("default_order_id") or self.env.context.get(
                "active_id"
            )
            if order_id and self.env.context.get("active_model") in (
                None, 
                "sale.order"
            ):
                values["order_id"] = order_id
        return values

    @api.depends("order_id")
    def _compute_display_invoice_alert(self):
        for wizard in self:
            wizard.display_invoice_alert = bool(
                wizard.order_id.invoice_ids.filtered(lambda inv: inv.state == "draft")
            )

    def action_cancel(self):
        self.order_id.update({"cancel_reason_id": self.reason_id.id})
        return self.order_id.with_context(disable_cancel_warning=True).action_cancel()
