# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    def prepare_sale_order_line_values(self, order, quantity, max_sequence=0):
        res = super().prepare_sale_order_line_values(
            order, quantity, max_sequence=max_sequence
        )
        if self.product_packaging_id:
            res["product_packaging_id"] = self.product_packaging_id.id
        return res
