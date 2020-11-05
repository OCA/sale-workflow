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
        return self.coupon_ids.filtered(lambda r: r.multi_use)

    @api.constrains("discount_fixed_amount")
    def _check_discount_fixed_amount(self):
        for rec in self:
            if rec._get_multi_use_coupons():
                raise ValidationError(
                    _(
                        "Fixed Amount can't be changed when there are Multi Use "
                        "coupons already."
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
