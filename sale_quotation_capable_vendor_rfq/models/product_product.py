# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_matching_vendor_pricelists(self, quantity, days_min=0, days_max=0):
        """
        Returns a recordset of product.supplierinfo records that match the criteria.

        :param quantity: Quantity to match
        :param days_min: Minimum delivery time to match
        :param days_max: Maximum delivery time to match
        :return: Recordset of product.supplierinfo
        """
        self.ensure_one()

        # get all vendors that match the criteria
        supplierinfo = self.seller_ids.filtered(
            lambda s: (not days_min or s.delay >= days_min)
            and (not days_max or s.delay <= days_max)
            and s.min_qty <= quantity
            and (s.product_id == self or not s.product_id)
        )

        # get the lowest price from each vendor
        min_prices = {}
        for info in supplierinfo:
            if info.partner_id not in min_prices:
                min_prices[info.partner_id] = info
            else:
                if info.price < min_prices[info.partner_id].price:
                    min_prices[info.partner_id] = info
        return self.env["product.supplierinfo"].concat(*min_prices.values())
