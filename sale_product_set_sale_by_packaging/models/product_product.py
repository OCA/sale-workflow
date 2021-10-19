# Copyright 2021 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_view_product_set_lines_to_check(self):
        action = self.product_tmpl_id.action_view_product_set_lines_to_check()
        action["context"] = {"default_product_id": self.id}
        return action
