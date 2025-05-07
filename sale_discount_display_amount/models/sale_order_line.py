# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    discount_total = fields.Monetary(
        compute="_compute_discount_total",
        string="Discount Subtotal",
        store=True,
        precompute=True,
    )
    price_total_no_discount = fields.Monetary(
        compute="_compute_discount_total",
        string="Subtotal Without Discount",
        store=True,
        precompute=True,
    )

    def _update_discount_display_fields(self):
        for line in self:
            price_total_no_discount = 0.0
            discount_total = 0.0
            currency = line.order_id.currency_id
            if not line.discount:
                price_total_no_discount = line.price_total
            else:
                price = line.price_unit
                taxes = line.tax_id.compute_all(
                    price,
                    currency,
                    line.product_uom_qty,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id,
                )

                price_total_no_discount = taxes["total_included"]
                discount_total = price_total_no_discount - line.price_total
            if (
                float_compare(
                    line.discount_total,
                    discount_total,
                    precision_rounding=currency.rounding,
                )
                != 0
            ):
                line.discount_total = discount_total
            if (
                float_compare(
                    line.price_total_no_discount,
                    price_total_no_discount,
                    precision_rounding=currency.rounding,
                )
                != 0
            ):
                line.price_total_no_discount = price_total_no_discount

    @api.depends(
        "discount",
        "price_total",
        "product_uom_qty",
        "product_id",
        "tax_id",
        "price_unit",
        "order_id.currency_id",
        "order_id.partner_shipping_id",
    )
    def _compute_discount_total(self):
        # we should move the logic from the _update_discount_display_fields
        # to the _compute_discount_total method but to ensure the backward
        # compatibility we keep the logic in both methods TODO in V19
        self._update_discount_display_fields()
