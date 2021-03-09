# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleCouponConsumptionLine(models.Model):
    """Model that stores data for single coupon multiple uses."""

    _name = "sale.coupon.consumption_line"
    _description = "Sale Coupon Consumption Line"

    coupon_id = fields.Many2one(comodel_name="sale.coupon", required=True, index=True)
    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line", required=True, ondelete="restrict"
    )
    sale_order_state = fields.Selection(related="sale_order_line_id.order_id.state")
    currency_program_id = fields.Many2one(related="coupon_id.program_id.currency_id")
    amount = fields.Float(digits="Product Price", currency_field="currency_program_id")

    def unlink(self):
        # Get the coupons before removing line
        coupons = self.mapped("coupon_id")
        result = super().unlink()
        # Update related coupons states if needed
        coupons.check_and_update_coupon_state()
        return result
