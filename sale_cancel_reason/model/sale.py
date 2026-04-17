# Copyright 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2022 Aritz Olea, Landoo SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models
from odoo.exceptions import UserError

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

    def action_draft(self):
        res = super().action_draft()
        self.write({"cancel_reason_id": False})
        return res

    def action_cancel(self):
        """Cancel SO after showing the cancel wizard when needed.
        (cfr :meth:`_show_cancel_wizard`)
        For post-cancel operations, please only override :meth:`_action_cancel`.
        note: self.ensure_one() if the wizard is shown.
        """
        if any(order.locked for order in self):
            raise UserError(
                _(
                    "You cannot cancel a locked order. \
                Please unlock it first."
                )
            )
        cancel_warning = self._show_cancel_wizard()
        if cancel_warning:
            self.ensure_one()

            return {
                "name": _("Cancel %s", self.type_name),
                "view_mode": "form",
                "res_model": "sale.order.cancel",
                "view_id": self.env.ref(
                    "sale_cancel_reason.sale_order_cancel_view_form"
                ).id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {
                    **self.env.context,
                    "default_order_id": self.id,
                    # "active_id": self.id,
                    # "active_ids": self.ids,
                    # "active_model": "sale.order",
                },
            }
        else:
            return self._action_cancel()

    def _show_cancel_wizard(self):
        """Decide whether the sale.order.cancel wizard
        should be shown to cancel specified orders.
        :return: True if there is any non-draft order in the given orders
        :rtype: bool
        """
        if self.env.context.get("disable_cancel_warning"):
            return False
        return any(so.state != "draft" for so in self)


class SaleOrderCancelReason(models.Model):
    _name = "sale.order.cancel.reason"
    _description = "Sale Order Cancel Reason"

    name = fields.Char("Reason", required=True, translate=True)
