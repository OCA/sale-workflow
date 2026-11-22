# Copyright 2025 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    quantity_restriction_id = fields.Many2one(
        "sale.quantity.restriction",
        string="Applied Restriction Rule",
        related="product_id.quantity_restriction_id",
    )

    warning_sale_qty = fields.Boolean(
        compute="_compute_warning_sale_qty", store=False, string="Quantity Visual Alert"
    )

    def _get_product_qty_in_product_unit(self):
        self.ensure_one()
        return self.product_uom._compute_quantity(
            self.product_uom_qty, self.product_id.uom_id
        )

    @api.depends("product_uom_qty", "quantity_restriction_id")
    def _compute_warning_sale_qty(self):
        """Calculates if a non-blocking warning should be displayed."""
        for line in self:
            line.warning_sale_qty = False
            restriction = line.quantity_restriction_id
            qty = line._get_product_qty_in_product_unit()

            if not restriction or not qty:
                continue

            # Check NON-MANDATORY rules
            is_min_warning = (
                restriction.min_qty > 0
                and not restriction.is_min_mandatory
                and qty < restriction.min_qty
            )
            is_max_warning = (
                restriction.max_qty > 0
                and not restriction.is_max_mandatory
                and qty > restriction.max_qty
            )
            is_multiple_warning = (
                restriction.multiple_qty > 1
                and not restriction.is_multiple_mandatory
                and (qty % restriction.multiple_qty != 0)
            )

            if is_min_warning or is_max_warning or is_multiple_warning:
                line.warning_sale_qty = True

    def _get_message_for_mandatory_restriction(self):
        """Checks mandatory restrictions on the line and returns the error message
        if one is violated."""
        self.ensure_one()
        restriction = self.quantity_restriction_id
        qty = self._get_product_qty_in_product_unit()

        if not restriction or not qty:
            return ""

        product_name = self.product_id.name

        # Mandatory Minimum
        if (
            restriction.min_qty > 0
            and restriction.is_min_mandatory
            and qty < restriction.min_qty
        ):
            return (
                f"The quantity ({qty}) is lower than the MANDATORY minimum "
                f"quantity of {restriction.min_qty} for product '{product_name}'."
            )

        # Mandatory Maximum
        if (
            restriction.max_qty > 0
            and restriction.is_max_mandatory
            and qty > restriction.max_qty
        ):
            return (
                f"The quantity ({qty}) is higher than the MANDATORY maximum "
                f"quantity of {restriction.max_qty} for product '{product_name}'."
            )

        # Mandatory Multiple
        if (
            restriction.multiple_qty > 1
            and restriction.is_multiple_mandatory
            and (qty % restriction.multiple_qty != 0)
        ):
            return (
                f"The quantity ({qty}) must be a MANDATORY multiple "
                f"of {restriction.multiple_qty} for product '{product_name}'."
            )

        return ""

    @api.constrains("product_uom_qty")
    def _check_mandatory_quantity_restrictions(self):
        for line in self:
            message = line._get_message_for_mandatory_restriction()
            if message:
                raise ValidationError(message)

    @api.onchange("product_uom_qty")
    def _onchange_product_uom_qty_restriction(self):
        """Triggers an immediate error message if a MANDATORY restriction is violated"""
        message = self._get_message_for_mandatory_restriction()
        if not message:
            return {}

        self.product_uom_qty = self._origin.product_uom_qty

        return {
            "warning": {
                "title": _("Warning for %s", self.product_id.name),
                "message": message,
            }
        }
