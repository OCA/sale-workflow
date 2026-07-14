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

    # This hook method determines if a discount is applied to the sale order line.
    # It provides an extension point (a "hook") for other modules to easily
    # modify the behavior of the discount calculation without directly altering
    # this module's code. For example, if a module like "sale_triple_discount"
    # introduces more complex discount logic (e.g., global discounts, tiered discounts),
    # it can override this method to correctly reflect whether a discount applies,
    # thereby influencing the 'discount_total' and 'price_total_no_discount' computations.
    def _has_discount(self):
        self.ensure_one()
        currency = self.currency_id or self.env.company.currency_id
        return not currency.is_zero(self.discount)

    def _update_discount_display_fields(self):
        for line in self:
            price_total_no_discount = 0.0
            discount_total = 0.0
            currency = line.order_id.currency_id or self.env.company.currency_id
            if not line._has_discount():
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
