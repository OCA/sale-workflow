# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.onchange("product_id")
    def onchange_product_id(self):
        # Only for action product_supplierinfo_type_action, called from purchase menu
        if "visible_product_tmpl_id" in self.env.context:
            self.product_tmpl_id = self.product_id.product_tmpl_id
