from odoo import fields, models


class SaleCouponGenerate(models.TransientModel):
    """Extend to add custom coupon code generation options."""

    _inherit = "sale.coupon.generate"

    custom_code_generation = fields.Boolean("Custom Code Generation")
    custom_code_prefix = fields.Char("Custom Code Prefix")
    custom_code_nbr = fields.Integer("Number of Alphanumeric symbols", default=5)

    def generate_coupon(self):
        """Override to pass custom_code_rule via context if needed."""
        if self.custom_code_generation:
            prefix = self.custom_code_prefix or ""
            self = self.with_context(custom_code_rule=(prefix, self.custom_code_nbr))
        return super(SaleCouponGenerate, self).generate_coupon()
