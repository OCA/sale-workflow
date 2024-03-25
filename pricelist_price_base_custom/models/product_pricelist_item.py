# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    base = fields.Selection(
        selection_add=[("custom_value", "Custom Value")],
        ondelete={"custom_value": "set default"},
    )

    def _compute_base_price(self, product, quantity, uom, date, target_currency):
        """
        Override to use custom base price if "custom_value"
        is selected as rule base and custom_base_price is
        passed in context
        """
        if self.base == "custom_value":
            return (
                self.env.context["custom_base_price"]
                if "custom_base_price" in self.env.context
                else 0.0
            )
        return super()._compute_base_price(
            product, quantity, uom, date, target_currency
        )
