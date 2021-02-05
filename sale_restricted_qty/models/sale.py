# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_warning_message = fields.Char(compute="_compute_qty_validity")
    qty_validity = fields.Boolean(compute="_compute_qty_validity")

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

    def _compute_qty_validity(self):
        for line in self:
            rounding = line.product_uom.rounding
            product_qty = line.product_uom._compute_quantity(
                line.product_uom_qty, line.product_id.uom_id
            )
            too_low = line.sale_min_qty and (
                float_compare(
                    product_qty, line.sale_min_qty, precision_rounding=rounding
                )
                < 0
            )
            too_high = line.sale_max_qty and (
                float_compare(
                    product_qty, line.sale_max_qty, precision_rounding=rounding
                )
                > 0
            )
            incorrect_multiple = (
                line.sale_multiple_qty > 0 and product_qty % line.sale_multiple_qty != 0
            )
            line.qty_validity = not (too_low or too_high or incorrect_multiple)
            if not line.qty_validity:
                message = ""
                if too_high:
                    if line.force_sale_min_qty:
                        message = _("Higher quantity recommended!")
                    else:
                        message = _("Higher quantity required!")
                if too_low:
                    if self.force_sale_max_qty:
                        message = _("Lower quantity recommended!")
                    else:
                        message = _("Lower quantity required!")
                if incorrect_multiple:
                    message += _("\nCorrect multiple of quantity required!")
                line.qty_warning_message = message

    # @api.constrains(
    #     "product_uom_qty", "sale_min_qty", "sale_max_qty", "sale_multiple_qty"
    # )
    # def check_constraint_restricted_qty(self):
    #     message = ""
    #     too_high = self.filtered(
    #         lambda r: "too_high" in r.qty_validity and not r.force_sale_max_qty
    #     ).mapped("product_id")
    #     too_low = self.filtered(
    #         lambda r: "too_low" in r.qty_validity and not r.force_sale_min_qty
    #     ).mapped("product_id")
    #     incorrect_multiple = self.filtered(
    #         lambda r: "incorrect_multiple" in r.qty_validity
    #     ).mapped("product_id")
    #     if too_low:
    #         message += _(
    #             "These products have a minimum order quantity: * \n"
    #         ) + "\n ".join(
    #             [
    #                 product.name + ": " + str(product.sale_min_qty)
    #                 for product in too_low
    #             ]
    #         )
    #         message += _(
    #             "\n* Check 'Force min quantity' if you want to bypass this rule"
    #         )
    #     if too_high:
    #         message += _(
    #             "These products have a maximum order quantity: * \n"
    #         ) + "\n ".join(
    #             [
    #                 product.name + ": " + str(product.sale_max_qty)
    #                 for product in too_high
    #             ]
    #         )
    #         message += _(
    #             "\n* Check 'Force max quantity' if you want to bypass this rule"
    #         )
    #     if incorrect_multiple:
    #         message += _(
    #             "These products must have correct quantity multiples: * \n"
    #         ) + "\n ".join(
    #             [
    #                 product.name + ": " + str(product.sale_multiple_qty)
    #                 for product in incorrect_multiple
    #             ]
    #         )
    #     if message:
    #         raise ValidationError(message)

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
