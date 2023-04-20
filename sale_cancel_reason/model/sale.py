# Copyright 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2022 Aritz Olea, Landoo SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    cancel_reason_id = fields.Many2one(
        "sale.order.cancel.reason",
        string="Reason for cancellation",
        readonly=True,
        ondelete="restrict",
        tracking=True,
        copy=False,
    )

    def _show_cancel_wizard(self):
        for order in self:
            if not order._context.get("disable_cancel_warning"):
                return True
        return False

    def action_draft(self):
        res = super().action_draft()
        self.write({"cancel_reason_id": False})
        return res


class SaleOrderCancelReason(models.Model):
    _name = "sale.order.cancel.reason"
    _description = "Sale Order Cancel Reason"

    name = fields.Char("Reason", required=True, translate=True)
