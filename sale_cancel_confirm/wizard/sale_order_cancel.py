# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderCancel(models.TransientModel):
    _inherit = "sale.order.cancel"

    sale_cancel_confirm = fields.Boolean(
        related="order_id.company_id.sale_cancel_confirm"
    )
    cancel_reason = fields.Text()

    def action_cancel(self):
        self.ensure_one()
        if self.sale_cancel_confirm:
            self.order_id.write(
                {
                    "cancel_confirm": True,
                    "cancel_reason": self.cancel_reason,
                    "cancel_by": self.env.user.id,
                    "cancel_date": fields.Date.context_today(self),
                }
            )
        return super().action_cancel()
