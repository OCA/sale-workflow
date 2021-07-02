# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _exception_product_brand_mixed(self):
        """Check if product brands are mixed in the same order"""
        self.ensure_one()
        brands = self.order_line.mapped("product_id.product_brand_id")
        return len(brands) > 1 and not all(brands.mapped("sale_order_mixed"))
