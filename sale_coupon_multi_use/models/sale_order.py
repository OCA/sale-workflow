# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrder(models.Model):
    """Extend to modify action_confirm for multi-use coupons."""

    _inherit = "sale.order"

    coupon_multi_use_ids = fields.Many2many(
        comodel_name="sale.coupon",
        compute="_compute_coupon_multi_use_ids",
        string="Multi Use Coupons",
    )

    @api.depends("order_line.coupon_consumption_line_ids")
    def _compute_coupon_multi_use_ids(self):
        for rec in self:
            rec.coupon_multi_use_ids = rec.mapped(
                "order_line.coupon_consumption_line_ids.coupon_id"
            )

    def _get_applied_programs(self):
        programs = super()._get_applied_programs()
        programs |= self.coupon_multi_use_ids.mapped("program_id")
        return programs

    def _get_valid_applied_coupon_program(self):
        programs = super()._get_valid_applied_coupon_program()
        add_programs = self.coupon_multi_use_ids.mapped("program_id")
        add_programs = add_programs._filter_programs_from_common_rules(self)
        return programs | add_programs

    def action_cancel(self):
        """Extend to remove lines from multi use coupons."""
        result = super().action_cancel()
        for order in self:
            lines_from_multi_use_coupon = order.order_line.filtered(
                "coupon_consumption_line_ids"
            )
            lines_from_multi_use_coupon.unlink()
        return result
