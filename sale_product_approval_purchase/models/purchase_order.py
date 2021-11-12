# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    approved_purchase = fields.Boolean(
        related="product_id.purchase_ok",
        string="Approved for Purchase",
        store=True,
        default=True,
    )


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    exceptions_purchase_approval = fields.Boolean(
        compute="_compute_exceptions", string="Exception", default=False
    )
    override_exception = fields.Boolean("Override Exception", default=False)

    @api.depends("order_line.approved_purchase")
    def _compute_exceptions(self):
        self.exceptions_purchase_approval = any(
            not line.approved_purchase for line in self.order_line
        )

    def _log_exception_activity_purchase(self, product_id):
        for order in self:
            note = self._render_product_state_excep(order, product_id)
            order.activity_schedule(
                "mail.mail_activity_data_warning",
                date.today(),
                note=note,
                user_id=order.user_id.id or SUPERUSER_ID,
            )

    def _render_product_state_excep(self, order, product_id):
        values = {"purchase_order_ref": order, "product_ref": product_id}
        return self.env.ref(
            "sale_product_approval_purchase.exception_on_product"
        )._render(values=values)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for purchase in self:
            if (
                purchase.exceptions_purchase_approval
                and not purchase.override_exception
                and not self._context.get("override_ex")
            ):
                raise UserError(
                    _(
                        "You can not confirm this purchase order "
                        "because some products are not purchasable in this order."
                    )
                )
        return res
