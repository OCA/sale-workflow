# Copyright 2022 Camptocamp SA
# @author: Damien Crier <damien.crier@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "product.mass.addition"]

    def _get_domain_add_products(self):
        return [("id", "in", self.season_allowed_product_ids.ids)]
