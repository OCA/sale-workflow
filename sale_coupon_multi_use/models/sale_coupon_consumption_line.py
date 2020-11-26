# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleCouponConsumptionLine(models.Model):
    """Model that stores data for single coupon multiple uses."""

    _name = "sale.coupon.consumption_line"
    _description = "Sale Coupon Consumption Line"

    coupon_id = fields.Many2one("sale.coupon", "Coupon", required=True, index=True)
    # ondelete takes care of automatically removing consumption line,
    # when discount line is removed on related sale order.
    sale_order_line_id = fields.Many2one(
        "sale.order.line", "Sale Order Line", required=True, ondelete="cascade"
    )
    currency_program_id = fields.Many2one(related="coupon_id.program_id.currency_id")
    amount = fields.Monetary(currency_field="currency_program_id")

    def _get_consumption_lines_to_unlink(self, order_lines):
        return self.filtered(lambda r: r.sale_order_line_id in order_lines)

    def _unlink_consumption_lines(self, order_lines):
        to_unlink = self._get_consumption_lines_to_unlink(order_lines)
        if to_unlink:
            to_unlink.with_context(force_unlink_coupon_consumption_lines=True).unlink()

    def unlink(self):
        """Override to prevent direct unlink."""
        if not self._context.get("force_unlink_coupon_consumption_lines"):
            raise UserError(
                _(
                    "Consumption Lines can't be deleted directly. To do that, "
                    "delete related sale order line."
                )
            )
        return super().unlink()
