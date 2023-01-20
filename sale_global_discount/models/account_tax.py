# Copyright 2023 Studio73 - Ferran Mora
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountTax(models.Model):
    _inherit = "account.tax"

    def _convert_to_tax_base_line_dict(
        self,
        base_line,
        partner=None,
        currency=None,
        product=None,
        taxes=None,
        price_unit=None,
        quantity=None,
        discount=None,
        account=None,
        analytic_distribution=None,
        price_subtotal=None,
        is_refund=False,
        rate=None,
        handle_price_include=True,
        extra_context=None,
    ):
        if (
            not isinstance(base_line, models.Model)
            or base_line._name != "sale.order.line"
            or not base_line.order_id.global_discount_ids
            or not self.env.context.get("from_tax_calculation", False)
        ):
            return super()._convert_to_tax_base_line_dict(
                base_line,
                partner,
                currency,
                product,
                taxes,
                price_unit,
                quantity,
                discount,
                account,
                analytic_distribution,
                price_subtotal,
                is_refund,
                rate,
                handle_price_include,
                extra_context,
            )
        discounts = base_line.order_id.global_discount_ids.mapped("discount")
        discounted_price_unit = price_unit
        if base_line.product_id.apply_global_discount:
            discounted_price_unit = base_line.order_id.get_discounted_global(
                price_unit, discounts.copy()
            )
        return super()._convert_to_tax_base_line_dict(
            base_line,
            partner,
            currency,
            product,
            taxes,
            discounted_price_unit,
            quantity,
            discount,
            account,
            analytic_distribution,
            price_subtotal,
            is_refund,
            rate,
            handle_price_include,
            extra_context,
        )
