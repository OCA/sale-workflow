# Copyright 2017-20 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends(
        "order_line.tax_id", "order_line.price_unit", "amount_total", "amount_untaxed"
    )
    def _compute_tax_totals_json(self):
        def compute_taxes(order_line):
            price = order_line.price_unit * (
                1 - (order_line.discount or 0.0) / 100.0
            ) - (order_line.discount_fixed or 0.0)
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
