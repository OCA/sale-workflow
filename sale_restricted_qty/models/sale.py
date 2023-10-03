# Copyright 2019 Akretion
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_min_qty = fields.Float(
        string="Min Qty",
        compute="_compute_sale_restricted_qty",
        store=True,
        digits="Product Unit of Measure",
    )
    force_sale_min_qty = fields.Boolean(
        compute="_compute_sale_restricted_qty", readonly=True, store=True
    )
    is_qty_less_min_qty = fields.Boolean(
        string="Qty < Min Qty", compute="_compute_is_qty_less_min_qty"
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
    is_qty_bigger_max_qty = fields.Boolean(
        string="Qty > max Qty", compute="_compute_is_qty_bigger_max_qty"
    )
    sale_multiple_qty = fields.Float(
        string="Multiple Qty",
        compute="_compute_sale_restricted_qty",
        store=True,
        digits="Product Unit of Measure",
    )
    is_qty_not_multiple_qty = fields.Boolean(
        string="Not Multiple Qty", compute="_compute_is_qty_not_multiple_qty"
    )

    @api.constrains(
        "product_uom_qty", "sale_min_qty", "sale_max_qty", "sale_multiple_qty"
    )
    def check_constraint_restricted_qty(self):

        msg = ""
        invaild_min_lines = []
        line_to_test = self.filtered(
            lambda sl: not sl.product_id.force_sale_min_qty and sl.is_qty_less_min_qty
        )
        for line in line_to_test:
            invaild_min_lines.append(
                _(
                    'Product "%(product)s": Min Quantity %(min_qty)s.',
                    product=line.product_id.name,
                    min_qty=line.sale_min_qty,
                )
            )

        if invaild_min_lines:
            msg += _(
                "Check minimum order quantity for this products: * \n"
            ) + "\n ".join(invaild_min_lines)
            msg += _(
                "\n* If you want sell quantity less than Min Quantity"
                ',Check "force min quatity" on product'
            )
        invaild_max_lines = []
        line_to_test = self.filtered(
            lambda sl: not sl.product_id.force_sale_max_qty and sl.is_qty_bigger_max_qty
        )
        for line in line_to_test:
            invaild_max_lines.append(
                _(
                    'Product "%(product)s": max Quantity %(max_qty)s.',
                    product=line.product_id.name,
                    max_qty=line.sale_max_qty,
                )
            )

        if invaild_max_lines:
            msg += _(
                "Check maximum order quantity for this products: * \n"
            ) + "\n ".join(invaild_max_lines)
            msg += _(
                "\n* If you want sell quantity bigger than max Quantity"
                ',Check "force max quatity" on product'
            )
        invaild_multiple_lines = []
        line_to_test = self.filtered(lambda sl: sl.is_qty_not_multiple_qty)
        for line in line_to_test:
            invaild_multiple_lines.append(
                _(
                    'Product "%(product)s": multiple Quantity %(multiple_qty)s.',
                    product=line.product_id.name,
                    multiple_qty=line.sale_multiple_qty,
                )
            )

        if invaild_multiple_lines:
            msg += _(
                "Check multiple order quantity for this products: * \n"
            ) + "\n ".join(invaild_multiple_lines)
            msg += _(
                "\n* If you want sell quantity not multiple Quantity"
                ",Set multiple quantity to 0 on product or product template"
                " or product category"
            )

        if msg:
            raise ValidationError(msg)

    def _get_product_qty_in_product_unit(self):
        self.ensure_one()
        return self.product_uom._compute_quantity(
            self.product_uom_qty, self.product_id.uom_id
        )

    @api.depends("product_id", "product_uom_qty", "sale_min_qty")
    def _compute_is_qty_less_min_qty(self):
        for line in self:
            rounding = line.product_uom.rounding
            product_qty = line._get_product_qty_in_product_unit()
            line.is_qty_less_min_qty = (
                line.sale_min_qty
                and (
                    float_compare(
                        product_qty, line.sale_min_qty, precision_rounding=rounding
                    )
                    < 0
                )
                or False
            )

    @api.depends("product_id", "product_uom_qty", "sale_max_qty")
    def _compute_is_qty_bigger_max_qty(self):
        for line in self:
            rounding = line.product_uom.rounding
            product_qty = line._get_product_qty_in_product_unit()
            line.is_qty_bigger_max_qty = (
                line.sale_max_qty
                and (
                    float_compare(
                        product_qty, line.sale_max_qty, precision_rounding=rounding
                    )
                    > 0
                )
                or False
            )

    @api.depends("product_id", "product_uom_qty", "sale_multiple_qty")
    def _compute_is_qty_not_multiple_qty(self):
        for line in self:
            product_qty = line.product_uom._compute_quantity(
                line.product_uom_qty, line.product_id.uom_id
            )
            line.is_qty_not_multiple_qty = (
                line.sale_multiple_qty > 0 and product_qty % line.sale_multiple_qty != 0
            )

    def _get_sale_restricted_qty(self):
        """Overridable function to change qty values (ex: form stock)"""
        self.ensure_one()
        res = {
            "sale_min_qty": (self.product_id and self.product_id.sale_min_qty or 0),
            "force_sale_min_qty": (
                self.product_id and self.product_id.force_sale_min_qty or False
            ),
            "sale_max_qty": (self.product_id and self.product_id.sale_max_qty or 0),
            "force_sale_max_qty": (
                self.product_id and self.product_id.force_sale_max_qty or False
            ),
            "sale_multiple_qty": (
                self.product_id and self.product_id.sale_multiple_qty or 0
            ),
        }
        return res

    @api.depends("product_id")
    def _compute_sale_restricted_qty(self):
        for rec in self:
            rec.update(rec._get_sale_restricted_qty())
