# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_matching_vendor_pricelists(self, quantity, output_time=0):
        """
        Returns a recordset of product.supplierinfo records that match the criteria.

        :param quantity: Quantity to match
        :param output_time: Integer of days to match
        :return: Recordset of product.supplierinfo
        """
        self.ensure_one()
        return self.seller_ids.filtered(
            lambda s: (not output_time or s.delay >= output_time)
            and s.min_qty <= quantity
        )
