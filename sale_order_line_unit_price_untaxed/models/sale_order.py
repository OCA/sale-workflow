# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_unit_untaxed = fields.Float(
        "Price without Taxes", compute="_compute_price_unit_untaxed", store=True
    )

    @api.depends("product_id", "price_unit", "tax_id")
    def _compute_price_unit_untaxed(self):
        """
        Use the compute_all method on tax to get the excluded price
        As this method uses the currency rounding and if price unit
        decimal precision is set to > currency one, the untaxed price
        can be too much rounded. So, use a memory record of currency
        with price unit decimal precision as rounding.
        """
        digits = self._fields["price_unit"].get_digits(self.env)
        rounding = (10 ** -digits[1]) if digits[1] else 0
        currencies = dict()
        for line in self:
            currency = line.order_id.currency_id
            if currency not in currencies:
                # Add the currency to saved ones in order to reuse it
                new_currency = self.env["res.currency"].new(currency.copy_data()[0])
                new_currency.rounding = rounding
                currencies[currency] = new_currency
            else:
                new_currency = currencies[currency]
            tot = line.tax_id.compute_all(
                line.price_unit,
                currency=new_currency,
                quantity=1,
                product=line.product_id,
            )
            line.price_unit_untaxed = tot["total_excluded"]
