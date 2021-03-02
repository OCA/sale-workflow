# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from math import fmod

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    qty_invalid = fields.Boolean(
        compute="_compute_qty_invalid", search="_search_qty_invalid"
    )

    def action_refresh_qty_restrictions(self):
        self.with_context(skip_constraint_sale_restrict_qty=True).mapped(
            "order_line"
        )._compute_qty_restrictions()

    @api.depends("order_line")
    def _compute_qty_invalid(self):
        for rec in self:
            rec.qty_invalid = any(rec.order_line.mapped("qty_invalid"))

    @api.model
    def _search_qty_invalid(self, operator, value):
        if operator not in ("=",):
            raise ValidationError(_("Invalid operator %s" % operator))
        if value not in (True, False):
            raise ValidationError(_("Invalid value %s" % operator))
        sale_orders = (
            self.env["sale.order.line"]
            .search([("qty_invalid", "=", value)])
            .mapped("order_id")
        )
        return [("id", "in", sale_orders.ids)]


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_warning_message = fields.Char(compute="_compute_qty_restrictions", store=True)
    qty_invalid = fields.Boolean(compute="_compute_qty_restrictions", store=True)

    sale_min_qty = fields.Float(
        string="Min Qty",
        compute="_compute_qty_restrictions",
        store=True,
        digits="Product Unit of Measure",
    )
    force_sale_min_qty = fields.Boolean(
        compute="_compute_qty_restrictions", readonly=True, store=True
    )
    sale_max_qty = fields.Float(
        string="Max Qty",
        compute="_compute_qty_restrictions",
        store=True,
        digits="Product Unit of Measure",
    )
    force_sale_max_qty = fields.Boolean(
        compute="_compute_qty_restrictions", readonly=True, store=True
    )
    sale_multiple_qty = fields.Float(
        string="Multiple Qty",
        compute="_compute_qty_restrictions",
        store=True,
        digits="Product Unit of Measure",
    )

    @api.depends(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "sale_max_qty",
        "sale_min_qty",
        "sale_multiple_qty",
    )
    def _compute_qty_restrictions(self):
        self._compute_sale_restricted_qty()
        self._compute_qty_validity()

    def _get_product_qty_in_product_unit(self):
        self.ensure_one()
        return self.product_uom._compute_quantity(
            self.product_uom_qty, self.product_id.uom_id
        )

    def _compute_qty_validity(self):
        for line in self:
            product_qty = line._get_product_qty_in_product_unit()

            def compare(qty):
                return qty and float_compare(
                    product_qty, qty, precision_rounding=line.product_uom.rounding
                )

            message = ""
            invalid = False
            if compare(line.sale_min_qty) < 0:
                if line.force_sale_min_qty:
                    message = _("Higher quantity recommended!")
                else:
                    invalid = True
                    message = _("Higher quantity required!")
            elif compare(line.sale_max_qty) > 0:
                if line.force_sale_max_qty:
                    message = _("Lower quantity recommended!")
                else:
                    invalid = True
                    message = _("Lower quantity required!")
            if line.sale_multiple_qty:
                rest_raw = fmod(product_qty, line.sale_multiple_qty)
                rest = float_compare(
                    rest_raw, 0.00, precision_rounding=line.product_uom.rounding
                )
                if rest:
                    invalid = True
                    message += _("\nCorrect multiple of quantity required!")
            line.qty_invalid = invalid
            line.qty_warning_message = message

    def _compute_sale_restricted_qty(self):
        for rec in self:
            rec.update(rec._get_sale_restricted_qty())

    @api.constrains(
        "product_uom_qty", "sale_min_qty", "sale_max_qty", "sale_multiple_qty"
    )
    def check_constraint_restricted_qty(self):
        if self.env.context.get("skip_constraint_sale_restrict_qty"):
            return
        self._compute_qty_validity()
        error_lines = self.filtered("qty_invalid")
        if error_lines:
            raise ValidationError(
                "\n".join(
                    [
                        f"{line.product_id.name} error: {line.qty_warning_message}"
                        for line in error_lines
                    ]
                )
            )

    def _get_sale_restricted_qty(self):
        """Overridable function to change qty values (ex: form stock)"""
        self.ensure_one()
        res = {
            "sale_min_qty": self.product_id.sale_min_qty,
            "force_sale_min_qty": self.product_id.force_sale_min_qty,
            "sale_max_qty": self.product_id.sale_max_qty,
            "force_sale_max_qty": self.product_id.force_sale_max_qty,
            "sale_multiple_qty": self.product_id.sale_multiple_qty,
        }
        return res
