from odoo import fields, models


class SaleMassCancelOrders(models.TransientModel):
    _inherit = "sale.mass.cancel.orders"

    reason_id = fields.Many2one(
        "sale.order.cancel.reason", string="Reason", required=True
    )

    def action_mass_cancel(self):
        self.sale_order_ids.write({"cancel_reason_id": self.reason_id.id})
        return super().action_mass_cancel()
