# Copyright 2019 Simone Rubino - Agile Business Group
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import contextlib
import operator
from functools import reduce

from odoo import api, fields, models
from odoo.tools import float_is_zero

# Map the rule's computation method to the name of the field used for the discount.
COMPUTE_PRICE_TO_DISCOUNT_FIELD = {
    "percentage": "percent_price",
    "formula": "price_discount",
}


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    discount2 = fields.Float(
        string="Discount 2 (%)",
        help="Second discount applied on a sale order line.",
        digits="Discount",
    )

    discount3 = fields.Float(
        string="Discount 3 (%)",
        help="Third discount applied on a sale order line.",
        digits="Discount",
    )

    def _get_triple_discounts_perc(self):
        """Return the list of discounts percentages to be applied."""
        self.ensure_one()
        discount_fields = self.env["sale.order.line"]._discount_fields()
        item_discount_field = COMPUTE_PRICE_TO_DISCOUNT_FIELD.get(self.compute_price)
        if item_discount_field is not None:
            discount_index = discount_fields.index("discount")
            discount_fields[discount_index] = item_discount_field

        # Exclude discounts that are 0 according to their precision
        discount_fields_digits = self.fields_get(
            allfields=discount_fields,
            attributes=[
                "digits",
            ],
        )
        discounts_perc = []
        for discount_field, attributes in discount_fields_digits.items():
            discount_perc = self[discount_field] or 0
            discount_digits = attributes.get("digits")
            if discount_digits is not None:
                all_digits, precision_digits = discount_digits
                is_zero = float_is_zero(
                    discount_perc,
                    precision_digits=precision_digits,
                )
            else:
                is_zero = discount_perc == 0

            if not is_zero:
                discounts_perc.append(discount_perc)
        return discounts_perc

    def _get_triple_discount(self):
        """Return the discount percentage represented by all the discounts."""
        self.ensure_one()
        discounts_perc = self._get_triple_discounts_perc()
        discounts = [1 - discount_perc / 100 for discount_perc in discounts_perc]
        triple_discount = reduce(operator.mul, discounts, 1)
        triple_discount = 100 - triple_discount * 100
        return triple_discount

    @contextlib.contextmanager
    def _patch_triple_discount(self):
        """Use the triple discount instead of the standard discount."""
        # Save the original discount of each rule
        item_to_original_discount = {}
        for item in self:
            item_discount_field = COMPUTE_PRICE_TO_DISCOUNT_FIELD.get(
                item.compute_price
            )
            if item_discount_field is not None:
                original_discount = item[item_discount_field]
                item_to_original_discount[item] = original_discount
                item.sudo()[item_discount_field] = item._get_triple_discount()

        yield

        # Restore the original discount in each updated rule
        for item, original_discount in item_to_original_discount.items():
            item_discount_field = COMPUTE_PRICE_TO_DISCOUNT_FIELD.get(
                item.compute_price
            )
            item.sudo()[item_discount_field] = original_discount

    def _compute_price(self, product, quantity, uom, date, currency=None):
        with self._patch_triple_discount():
            return super()._compute_price(
                product,
                quantity,
                uom,
                date,
                currency=currency,
            )

    @api.depends(
        "discount2",
        "discount3",
    )
    def _compute_rule_tip(self):
        with self._patch_triple_discount():
            return super()._compute_rule_tip()

    @api.depends(
        "discount2",
        "discount3",
    )
    def _compute_name_and_price(self):
        with self._patch_triple_discount():
            return super()._compute_name_and_price()
