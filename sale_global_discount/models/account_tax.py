# Copyright 2023 Studio73 - Ferran Mora
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountTax(models.Model):
    _inherit = "account.tax"

    def _prepare_base_line_for_taxes_computation(self, record, **kwargs):
        if (
            not isinstance(record, models.Model)
            or record._name != "sale.order.line"
            or not record.order_id.global_discount_ids
            or not self.env.context.get("from_tax_calculation", False)
        ):
            return super()._prepare_base_line_for_taxes_computation(record, **kwargs)

        price_unit = kwargs.get("price_unit", 0.0)
        discounted_price_unit = price_unit
        if not record.product_id.bypass_global_discount:
            discounts = record.order_id.global_discount_ids.mapped("discount")
            discounted_price_unit = record.order_id.get_discounted_global(
                price_unit, discounts.copy()
            )
        kwargs.update({"price_unit": discounted_price_unit})
        return super()._prepare_base_line_for_taxes_computation(record, **kwargs)
