# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "base.cancel.confirm"]

    _has_cancel_reason = "optional"  # ["no", "optional", "required"]

    cancel_confirm = fields.Boolean(default=False)

    def _show_cancel_wizard(self):
        if self.env.context.get("disable_cancel_warning"):
            return False
        return super()._show_cancel_wizard() or any(
            order.company_id.sale_cancel_confirm for order in self
        )

    def action_draft(self):
        res = super().action_draft()
        self.clear_cancel_confirm_data()
        return res
