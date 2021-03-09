# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleCouponProgram(models.Model):
    """Extend to add logic that control multi coupon usage."""

    _inherit = "sale.coupon.program"

    @api.constrains("currency_custom_id")
    def _check_currency_custom_id(self):
        for rec in self:
            if rec.coupon_multi_use and rec.coupon_ids:
                raise ValidationError(
                    _(
                        "Currency can't be changed when there are Multi"
                        " Use coupons already."
                    )
                )
