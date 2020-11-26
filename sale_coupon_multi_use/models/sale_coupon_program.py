# Copyright 2020 Camptocamp SA
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

    @api.onchange("coupon_multi_use")
    def _onchange_coupon_multi_use(self):
        if self.coupon_multi_use:
            self.update(self._prepare_multi_use_vals())

    def _get_multi_use_coupons(self):
        self.ensure_one()
        return self.coupon_ids.filtered("multi_use")

    @api.constrains("discount_fixed_amount")
    def _check_discount_fixed_amount(self):
        for rec in self:
            if rec._get_multi_use_coupons():
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
                rec.coupon_multi_use or rec._get_multi_use_coupons()
            ) and not rec._validate_coupon_multi_use_field_values():
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
        coupon_code = self._context.get("coupon_code")
        sale_order = self._context.get("coupon_sale_order")
        if coupon_code and sale_order and field == "discount_fixed_amount":
            multi_use_coupon = self.env["sale.coupon"].search(
                [
                    ("multi_use", "=", True),
                    ("code", "=", coupon_code),
                    ("state", "=", "new"),
                ],
                limit=1,
            )
            if multi_use_coupon:
                return self._compute_program_multi_use_amount(
                    multi_use_coupon, sale_order, currency_to
                )

        return super()._compute_program_amount(field, currency_to)
