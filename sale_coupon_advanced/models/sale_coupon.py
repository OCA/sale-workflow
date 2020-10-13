import secrets
import string

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleCoupon(models.Model):
    """Extend to implement custom code generation rule."""

    _inherit = "sale.coupon"

    # Must overwrite here for override method to take effect.
    code = fields.Char(default=lambda s: s._generate_code())

    def _validate_custom_code_rule(self, custom_code_rule):
        if custom_code_rule[1] < 1:
            raise UserError(
                _(
                    "Custom Code Rule Must have at least one random "
                    "alphanumeric symbol"
                )
            )

    def _generate_custom_code(self, custom_code_rule):
        alphabet = string.ascii_letters + string.digits
        prefix, nbr = custom_code_rule
        code = "".join(secrets.choice(alphabet) for i in range(nbr))
        return "{}{}".format(prefix, code)

    @api.model
    def _generate_code(self):
        """Override to handle custom_code_rule from context."""
        custom_code_rule = self._context.get("custom_code_rule")
        if custom_code_rule:
            self._validate_custom_code_rule(custom_code_rule)
            return self._generate_custom_code(custom_code_rule)
        return super()._generate_code()
