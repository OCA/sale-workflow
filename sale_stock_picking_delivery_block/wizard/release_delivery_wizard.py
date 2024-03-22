from odoo import _, fields, models


class SaleReleaseDelivery(models.TransientModel):
    _name = "sale.release.delivery.wizard"
    _description = "Wizard before releasing delivery"

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        required=True,
        default=lambda self: self.env.context.get("active_id", False),
    )
    log_reason = fields.Text(string="Reason")

    def action_release_delivery(self):
        self.ensure_one()
        self.sale_id.block_delivery = False
        # log a message on the sale order
        self.sale_id.message_post(
            body=_("Delivery released by %(user)s: %(reason)s")
            % {
                "user": self.env.user.name,
                "reason": self.log_reason,
            }
        )
        return True
