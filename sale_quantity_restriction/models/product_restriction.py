# Copyright 2025 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ProductQuantityRestriction(models.Model):
    _name = "sale.quantity.restriction"
    _description = "Sale Quantity Restriction"

    name = fields.Char(string="Nom de la Règle", compute="_compute_name", store=True)

    min_qty = fields.Float(string="Minimum Quantity")
    is_min_mandatory = fields.Boolean(string="Minimum Mandatory?")

    max_qty = fields.Float(string="Maximum Quantity")
    is_max_mandatory = fields.Boolean(string="Maximum Mandatory?")

    multiple_qty = fields.Float(string="Multiple of Quantity")
    is_multiple_mandatory = fields.Boolean(string="Multiple Mandatory?")

    product_tmpl_ids = fields.One2many(
        "product.template", "manual_quantity_restriction_id", string="Products"
    )
    category_ids = fields.One2many(
        "product.category",
        "manual_quantity_restriction_id",
        string="Product Categories",
    )

    @api.depends(
        "min_qty",
        "is_min_mandatory",
        "max_qty",
        "is_max_mandatory",
        "multiple_qty",
        "is_multiple_mandatory",
    )
    def _compute_name(self):
        """Computes a descriptive name for the restriction based on its settings."""
        for rule in self:
            parts = []

            def format_qty(qty):
                # Trailing .O is suppressed : 10.0 -> "10", 10.5 -> "10.5"
                return f"{qty:g}"

            if rule.min_qty > 0:
                min_str = _("Min: %s", format_qty(rule.min_qty))
                if rule.is_min_mandatory:
                    min_str += _(" (M)")  # M for Mandatory
                parts.append(min_str)

            if rule.max_qty > 0:
                max_str = _("Max: %s", format_qty(rule.max_qty))
                if rule.is_max_mandatory:
                    max_str += _(" (M)")
                parts.append(max_str)

            if rule.multiple_qty > 1:
                multiple_str = _("Multiple: %s", format_qty(rule.multiple_qty))
                if rule.is_multiple_mandatory:
                    multiple_str += _(" (M)")
                parts.append(multiple_str)

            if parts:
                rule.name = ", ".join(parts)
            else:
                rule.name = _("No Restriction")
