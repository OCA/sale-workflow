from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_method_id = fields.Many2one(
        "account.payment.method",
        string="Payment Method",
        ondelete="restrict",
    )

    def auto_set_invoice_block(self):
        recs = self.filtered_domain(
            [("payment_method_id.hold_picking_until_payment", "=", True)]
        )

        if not recs:
            return

        block_reason = self.env.ref("sale_stock_picking_blocking.pay_before_delivery")

        # Block records that are not yet invoiced or draft
        # Unblock the rest
        block = recs.filtered_domain(
            [
                "|",
                "&",
                ("state", "=", "draft"),
                ("invoice_status", "=", "no"),
                ("invoice_status", "!=", "invoiced"),
            ]
        )

        unblock = recs - block

        block.write({"delivery_block_id": block_reason.id})
        unblock.action_remove_delivery_block()

    def onchange_partner_id(self):
        result = super().onchange_partner_id()

        self.auto_set_invoice_block()

        return result

    def _get_invoice_status(self):
        result = super()._get_invoice_status()

        self.auto_set_invoice_block()

        return result
