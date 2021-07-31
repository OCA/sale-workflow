# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def create_demo_and_validate(self):
        silo = self.env['stock.inventory.line']
        demo_inv = self.env.ref('sale_rental.rental_inventory')
        rental_in_loc = self.env.ref('stock.warehouse0').rental_in_location_id
        demo_inv.write({'location_ids': [(6, 0, [rental_in_loc.id])]})
        demo_inv.action_start()
        products = [
            ('product.consu_delivery_01', 56),
            ('product.product_product_20', 46),
            ('product.product_product_25', 2),
        ]
        for (product_xmlid, qty) in products:
            product = self.env.ref(product_xmlid)
            silo.create({
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'inventory_id': demo_inv.id,
                'product_qty': qty,
                'location_id': rental_in_loc.id,
            })
        demo_inv.action_validate()
