# Copyright 2019 Akretion
# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .product_restricted_qty_mixin import RESTRICTION_ENABLED


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_min_qty_set = fields.Boolean(
        compute="_compute_restricted_qty_from_product",
        store=True,
    )
    min_qty = fields.Float(
        help="The minimum quantity of product that can be sold.",
        compute="_compute_restricted_qty_from_product",
        store=True,
        digits="Product Unit of Measure",
    )
    restrict_min_qty = fields.Boolean(
        compute="_compute_restricted_qty_from_product",
        store=True,
    )
    is_below_min_qty = fields.Boolean(
        compute="_compute_restricted_qty_constraints",
    )

    is_max_qty_set = fields.Boolean(
        compute="_compute_restricted_qty_from_product",
        store=True,
    )
    max_qty = fields.Float(
        help="The maximum quantity of product that can be sold.",
        compute="_compute_restricted_qty_from_product",
        store=True,
        digits="Product Unit of Measure",
    )
    restrict_max_qty = fields.Boolean(
        compute="_compute_restricted_qty_from_product",
        store=True,
    )
    is_above_max_qty = fields.Boolean(
        compute="_compute_restricted_qty_constraints",
    )

    is_multiple_of_qty_set = fields.Boolean(
        compute="_compute_restricted_qty_from_product",
        store=True,
    )
    multiple_of_qty = fields.Float(
        string="Multiple-Of Qty",
        help="The multiple-of quantity of product that can be sold.",
        compute="_compute_restricted_qty_from_product",
        store=True,
        digits="Product Unit of Measure",
    )
    restrict_multiple_of_qty = fields.Boolean(
        compute="_compute_restricted_qty_from_product",
        store=True,
    )
    is_not_multiple_of_qty = fields.Boolean(
        compute="_compute_restricted_qty_constraints",
    )

    @api.depends(
        "product_id.is_sale_min_qty_set",
        "product_id.sale_min_qty",
        "product_id.sale_restrict_min_qty",
        "product_id.is_sale_max_qty_set",
        "product_id.sale_max_qty",
        "product_id.sale_restrict_max_qty",
        "product_id.is_sale_multiple_of_qty_set",
        "product_id.sale_multiple_of_qty",
        "product_id.sale_restrict_multiple_of_qty",
    )
    def _compute_restricted_qty_from_product(self):
        for line in self:
            line.is_min_qty_set = line.product_id.is_sale_min_qty_set
            line.min_qty = line.product_id.sale_min_qty
            line.restrict_min_qty = (
                line.product_id.sale_restrict_min_qty == RESTRICTION_ENABLED
            )

            line.is_max_qty_set = line.product_id.is_sale_max_qty_set
            line.max_qty = line.product_id.sale_max_qty
            line.restrict_max_qty = (
                line.product_id.sale_restrict_max_qty == RESTRICTION_ENABLED
            )

            line.is_multiple_of_qty_set = line.product_id.is_sale_multiple_of_qty_set
            line.multiple_of_qty = line.product_id.sale_multiple_of_qty
            line.restrict_multiple_of_qty = (
                line.product_id.sale_restrict_multiple_of_qty == RESTRICTION_ENABLED
            )

    @api.depends(
        "product_id.uom_id",
        "product_uom",
        "product_uom_qty",
        "is_min_qty_set",
        "min_qty",
        "is_max_qty_set",
        "max_qty",
        "is_multiple_of_qty_set",
        "multiple_of_qty",
    )
    def _compute_restricted_qty_constraints(self):
        for line in self:
            qty = line.product_uom._compute_quantity(
                line.product_uom_qty, line.product_id.uom_id
            )
            line.is_below_min_qty = line.is_min_qty_set and qty < line.min_qty
            line.is_above_max_qty = line.is_max_qty_set and qty > line.max_qty
            line.is_not_multiple_of_qty = line.is_multiple_of_qty_set and (
                line.multiple_of_qty != 0 and qty % line.multiple_of_qty != 0
            )

    @api.constrains(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "is_min_qty_set",
        "min_qty",
        "restrict_min_qty",
        "is_max_qty_set",
        "max_qty",
        "restrict_max_qty",
        "is_multiple_of_qty_set",
        "multiple_of_qty",
        "restrict_multiple_of_qty",
    )
    def check_restricted_qty(self):
        failed_lines = []
        for line in self:
            qty = line.product_uom._compute_quantity(
                line.product_uom_qty, line.product_id.uom_id
            )

            failed_constraints = []

            if line.is_min_qty_set and line.restrict_min_qty and qty < line.min_qty:
                failed_constraints.append(
                    _("minimal quantity is %(min_qty)s")
                    % {
                        "min_qty": line.min_qty,
                    }
                )

            if line.is_max_qty_set and line.restrict_max_qty and qty > line.max_qty:
                failed_constraints.append(
                    _("maximal quantity is %(max_qty)s")
                    % {
                        "max_qty": line.max_qty,
                    }
                )

            if (
                line.is_multiple_of_qty_set
                and line.restrict_multiple_of_qty
                and line.multiple_of_qty != 0
                and qty % line.multiple_of_qty != 0
            ):
                failed_constraints.append(
                    _("quantity should be multiple of %(multiple_of_qty)s")
                    % {
                        "multiple_of_qty": line.multiple_of_qty,
                    }
                )

            if failed_constraints:
                failed_lines.append(
                    _('Product "%(product_name)s": %(failed_constraints)s')
                    % {
                        "product_name": line.product_id.name,
                        "failed_constraints": ", ".join(failed_constraints),
                    }
                )

        if failed_lines:
            msg = _("Check quantity for these products:\n") + "\n".join(failed_lines)
            raise ValidationError(msg)
