# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from itertools import groupby

from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _create_cache_with_date__get_raw_values(self):
        values = []
        item_model = self.env["product.pricelist.item"]
        for pricelist in self:
            # 1) get items with dates, referencing products
            date_items = pricelist.item_ids.filtered(
                lambda i: (
                    i.applied_on == "0_product_variant"
                    and i.product_id
                    and (i.date_start or i.date_end)
                )
            )
            formula_items = pricelist.item_ids.filtered(
                lambda i: (
                    i.applied_on == "0_product_variant"
                    and i.product_id
                    and i.compute_price == "formula"
                    and (i.price_surcharge or i.price_discount)
                )
            )
            overlapping_parents = formula_items._get_overlapping_parent_items()
            # Formula items are altering price coming from the parent.
            # It means that each time price changes on the parent,
            # it should change on the current pricelist as well.
            # Therefore, we have to retrieve parent's overlapping items here.
            # 2) group by product
            items = date_items | formula_items | overlapping_parents
            items.sorted(lambda item: item.product_id.id)
            groups = groupby(items, key=lambda item: item.product_id.id)
            for product_id, item_list in groups:
                product_items = item_model.browse([i.id for i in item_list])
                date_ranges = product_items._get_not_overlapping_date_ranges()
                for date_start, date_end in date_ranges:
                    # We might have a False value (never starting or ending item)
                    at_date = date_start or date_end
                    product_price = pricelist._get_product_prices([product_id], at_date)
                    price = product_price[product_id]
                    values.append(
                        (
                            product_id,
                            pricelist.id,
                            price,
                            date_start or None,
                            date_end or None,
                        )
                    )
        return values
