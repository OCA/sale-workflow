from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_tx_id = fields.Many2one("payment.transaction", string="Last Transaction")
    payment_acquirer_id = fields.Many2one(
        "payment.acquirer",
        string="Payment Acquirer",
        related="payment_tx_id.acquirer_id",
        store=True,
    )
