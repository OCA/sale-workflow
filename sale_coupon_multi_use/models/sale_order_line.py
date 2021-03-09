# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    """Extend to reverse relate with consumption line."""

    _inherit = "sale.order.line"

    coupon_consumption_line_ids = fields.One2many(
        comodel_name="sale.coupon.consumption_line",
        inverse_name="sale_order_line_id",
        readonly=True,
    )

    def unlink(self):
        consumption_lines = self.mapped("coupon_consumption_line_ids")
        if consumption_lines:
            # Remove related consumption lines
            # Using sudo because no user can remove consumption lines
            consumption_lines.sudo().unlink()
        return super().unlink()
