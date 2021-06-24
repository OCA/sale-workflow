# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleCouponProgram(models.Model):
    """Extend to add logic that control multi coupon usage."""

    _inherit = "sale.coupon.program"

    coupon_multi_use = fields.Boolean("Multi Use Coupons")

    def _prepare_multi_use_vals(self):
        self.ensure_one()
        return {
            "program_type": "coupon_program",
            "reward_type": "discount",
            "discount_type": "fixed_amount",
        }

    def _check_can_change_coupon_multi_use(self):
        self.ensure_one()
        if self.coupon_ids:
            raise ValidationError(
                _("Coupon multi use can't be changed with existing coupons.")
            )

    @api.onchange("coupon_multi_use")
    def _onchange_coupon_multi_use(self):
        self._check_can_change_coupon_multi_use()
        if self.coupon_multi_use:
            self.update(self._prepare_multi_use_vals())

    def write(self, values):
        for program in self:
            if "coupon_multi_use" in values:
                program._check_can_change_coupon_multi_use()
        return super().write(values)

    @api.constrains("discount_fixed_amount")
    def _check_discount_fixed_amount(self):
        for rec in self:
            if rec.coupon_multi_use and rec.coupon_ids:
                raise ValidationError(
                    _(
                        "Fixed Amount can't be changed when there are Multi"
                        " Use coupons already."
                    )
                )

    def _validate_coupon_multi_use_field_values(self):
        self.ensure_one()
        for fname, value in self._prepare_multi_use_vals().items():
            if self[fname] != value:
                return False
        return True

    @api.constrains("coupon_multi_use", "reward_type", "discount_type", "program_type")
    def _check_coupon_multi_use_options(self):
        for rec in self:
            if (
                rec.coupon_multi_use
                and not rec._validate_coupon_multi_use_field_values()
            ):
                raise ValidationError(
                    _(
                        "Multi Use Coupons program must have Coupon Program Type, "
                        "Discount Reward and Fixed Amount as Apply Discount"
                    )
                )

    def _compute_program_multi_use_amount(
        self, multi_use_coupon, sale_order, currency_to
    ):
        # Only using remaining amount (original implementation
        # always uses full amount specified on related program).
        amount_delta = multi_use_coupon.discount_fixed_amount_delta
        amount_delta = self.currency_id._convert(
            amount_delta, currency_to, self.company_id, fields.Date.today()
        )
        return min(amount_delta, sale_order.amount_total)

    def _compute_program_amount(self, field, currency_to):
        """Extend to consume correct multi-use coupon amount."""
        self.ensure_one()
        if field != "discount_fixed_amount":
            # Just want to customize program amount
            # when compute the final dicsount
            return super()._compute_program_amount(field, currency_to)
        multi_use_coupon = self.env.context.get("multi_use_coupon")
        current_order = self.env.context.get("current_order")
        if not (self.coupon_multi_use and multi_use_coupon and current_order):
            return super()._compute_program_amount(field, currency_to)
        # Case of multi use
        return self._compute_program_multi_use_amount(
            multi_use_coupon, current_order, currency_to
        )

    def action_view_sales_orders(self):
        result = super().action_view_sales_orders()
        if self.coupon_multi_use:
            # Override domain to remove order state filter,
            # because for coupon multi use programs all sale orders count.
            # Canceled sale orders are not linked anymore to coupon,
            # because reward line is removed when cancel sale order.
            orders = self.mapped("coupon_ids.sale_multi_use_ids")
            result["domain"] = [("id", "in", orders.ids)]
        return result
