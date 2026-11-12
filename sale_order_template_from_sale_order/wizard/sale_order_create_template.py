# Copyright 2026 Cetmix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderCreateTemplate(models.TransientModel):
    _name = "sale.order.create.template"
    _description = "Create Sale Order Template from Sale Order"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        required=True,
        ondelete="cascade",
        default=lambda self: self._default_sale_order_id(),
    )
    name = fields.Char(required=True)

    @api.model
    def _default_sale_order_id(self):
        """Take the sales order the wizard was opened from.

        :return: active sales order id, or ``None`` when the wizard is not
            opened from an order
        :rtype: int or None
        """
        return self.env.context.get("active_id")

    def action_create_template(self):
        """Create the quotation template and close the wizard.

        The sales order is only read. The user stays on it.

        :return: client action that shows a success notification and closes
            the wizard
        :rtype: dict
        """
        self.ensure_one()
        template = self.env["sale.order.template"].create(
            self.sale_order_id._prepare_sale_order_template_vals(self.name)
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": self.env._(
                    "Template %(name)s is created", name=template.name
                ),
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
