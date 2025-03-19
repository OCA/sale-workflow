# Copyright 2025 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _assign_new_custom_variant(self):
        """Create new variants and assign them to the `self`."""
        for line in self:
            with line.product_id._get_attribute_custom_value_variant(
                line.product_custom_attribute_value_ids
            ) as new_variant:
                line.product_id = new_variant

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        custom_value_lines = lines.filtered("product_custom_attribute_value_ids")
        if custom_value_lines:
            custom_value_lines._assign_new_custom_variant()
        return lines
