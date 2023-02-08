from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_method_id = fields.Many2one(
        "account.payment.method",
        string="Payment Method",
        ondelete="restrict",
    )
    hold_picking_until_payment = fields.Boolean(
        related="payment_method_id.hold_picking_until_payment"
    )

    @api.model
    def create(self, vals):
        sale_order = super(SaleOrder, self).create(vals)
        if not sale_order.website_id:
            sale_order.hold_picking_until_payment = True
        return sale_order
