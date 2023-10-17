# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_domain_add_products(self):
        res = super()._get_domain_add_products()
        if self.has_allowed_products:
            res = expression.AND([res, [("id", "in", self.allowed_product_ids.ids)]])
        return res
