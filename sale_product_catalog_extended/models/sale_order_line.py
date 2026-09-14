# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _remove_catalog_last_sales_exclusions(self):
        """Drop the *Last sales* exclusions of these lines' products when their
        order is already confirmed, which the clean up done on confirmation
        cannot cover.

        Only the products of these lines are cleaned up: the ones already in the
        order were not sold again by this change.
        """
        for order, lines in self.grouped("order_id").items():
            if order.state != "sale":
                continue
            order._remove_catalog_last_sales_exclusions(products=lines.product_id)

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._remove_catalog_last_sales_exclusions()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if "product_id" in vals:
            self._remove_catalog_last_sales_exclusions()
        return res
