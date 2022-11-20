# Copyright 2017-20 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits="Product Price",
        help="Fixed amount discount.",
    )

    @api.onchange("discount")
    def _onchange_discount_percent(self):
        # _onchange_discount method already exists in core,
        # but discount is not in the onchange definition
        if self.discount:
            self.discount_fixed = 0.0

    @api.onchange("discount_fixed")
    def _onchange_discount_fixed(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.constrains("discount", "discount_fixed")
    def _check_only_one_discount(self):
        for line in self:
            if line.discount and line.discount_fixed:
                raise ValidationError(
                    _("You can only set one type of discount per line.")
                )

    @api.depends(
        "product_uom_qty", "discount", "price_unit", "tax_id", "discount_fixed"
    )
    def _compute_amount(self):
        vals = {}
        for line in self.filtered(
            lambda l: l.discount_fixed and l.order_id.state not in ["done", "cancel"]
        ):
            real_price = line.price_unit * (1 - (line.discount or 0.0) / 100.0) - (
                line.discount_fixed or 0.0
            )
            twicked_price = real_price / (1 - (line.discount or 0.0) / 100.0)
            vals[line] = {
                "price_unit": line.price_unit,
            }
            line.update({"price_unit": twicked_price})
        res = super(SaleOrderLine, self)._compute_amount()
        for line in vals.keys():
            line.update(vals[line])
        return res

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res.update({"discount_fixed": self.discount_fixed})
        return res


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends(
        "order_line.tax_id", "order_line.price_unit", "amount_total", "amount_untaxed"
    )
    def _compute_tax_totals_json(self):
        def compute_taxes(order_line):
            real_price = order_line.price_unit * (
                1 - (order_line.discount or 0.0) / 100.0
            ) - (order_line.discount_fixed or 0.0)
            twicked_price = real_price / (1 - (order_line.discount or 0.0) / 100.0)
            price = (
                order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
                if not order_line.discount_fixed
                else twicked_price
            )
            order = order_line.order_id
            return order_line.tax_id._origin.compute_all(
                price,
                order.currency_id,
                order_line.product_uom_qty,
                product=order_line.product_id,
                partner=order.partner_shipping_id,
            )

        account_move = self.env["account.move"]
        for order in self:
            tax_lines_data = (
                account_move._prepare_tax_lines_data_for_totals_from_object(
                    order.order_line, compute_taxes
                )
            )
            tax_totals = account_move._get_tax_totals(
                order.partner_id,
                tax_lines_data,
                order.amount_total,
                order.amount_untaxed,
                order.currency_id,
            )
            order.tax_totals_json = json.dumps(tax_totals)
