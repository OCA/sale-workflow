# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_warning_message = fields.Char(compute="_compute_qty_validity", store=True)
    qty_invalid = fields.Boolean(compute="_compute_qty_validity", store=True)

    sale_min_qty = fields.Float(
        string="Min Qty",
        compute="_compute_sale_restricted_qty",
        store=True,
        digits="Product Unit of Measure",
    )
    force_sale_min_qty = fields.Boolean(
        compute="_compute_sale_restricted_qty", readonly=True, store=True
    )
    sale_max_qty = fields.Float(
        string="Max Qty",
        compute="_compute_sale_restricted_qty",
        store=True,
        digits="Product Unit of Measure",
    )
    force_sale_max_qty = fields.Boolean(
        compute="_compute_sale_restricted_qty", readonly=True, store=True
    )
    sale_multiple_qty = fields.Float(
        string="Multiple Qty",
        compute="_compute_sale_restricted_qty",
        store=True,
        digits="Product Unit of Measure",
    )

    @api.depend(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "sale_max_qty",
        "sale_min_qty",
        "sale_multiple_qty",
    )
    def _compute_qty_validity(self):
        for line in self:
            product_qty = line.product_uom._compute_quantity(
                line.product_uom_qty, line.product_id.uom_id
            )

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
                if self.force_sale_max_qty:
                    message = _("Lower quantity recommended!")
                else:
                    invalid = True
                    message = _("Lower quantity required!")
            if line.sale_multiple_qty and not product_qty % line.sale_multiple_qty:
                invalid = True
                message += _("\nCorrect multiple of quantity required!")
            self.qty_invalid = invalid
            line.qty_warning_message = message

    @api.constrains(
        "product_uom_qty", "sale_min_qty", "sale_max_qty", "sale_multiple_qty"
    )
    def check_constraint_restricted_qty(self):
        if self.qty_invalid:
            raise ValidationError(self.qty_warning_message)

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

    @api.depends("product_id")
    def _compute_sale_restricted_qty(self):
        for rec in self:
            rec.update(rec._get_sale_restricted_qty())
