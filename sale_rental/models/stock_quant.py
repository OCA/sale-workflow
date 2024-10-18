# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockInventory(models.Model):
    _inherit = "stock.quant"

    @api.model
    def create_demo_and_validate(self):
        rental_in_loc = self.env.ref("stock.warehouse0").rental_in_location_id
        products = [
            ("product.consu_delivery_01", 56),
            ("product.product_product_20", 46),
            ("product.product_product_25", 2),
        ]
        for (product_xmlid, qty) in products:
            product = self.env.ref(product_xmlid)
            self.with_context(inventory_mode=True).create(
                {
                    "product_id": product.id,
                    "inventory_quantity": qty,
                    "location_id": rental_in_loc.id,
                }
            ).action_apply_inventory()
