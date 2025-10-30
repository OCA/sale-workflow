# Copyright 2025 Akretion (https://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_packaging")
    def _onchange_product_packaging(self):
        res = super()._onchange_product_packaging()
        print("### _onchange_product_packaging TRIGGERED", self.env.context)
        if self.product_packaging:
            self.with_context(packaging=self.product_packaging).product_uom_change()
        return res

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        # Initialiser self avec le contexte si un packaging est présent
        current_self = self
        if self.product_packaging and "packaging" not in self.env.context:
            current_self = self.with_context(packaging=self.product_packaging)

        res = super(SaleOrderLine, current_self).product_uom_change()

        if current_self.product_id and current_self.order_id.pricelist_id:
            
            qty_value = current_self.product_uom_qty or 1.0

            pricelist = current_self.order_id.pricelist_id.with_context(
                uom=current_self.product_uom.id,
                date=current_self.order_id.date_order,
            )

            try:
                products_list = [(current_self.product_id.id,)] 
                
                price_data = pricelist.price_get(
                    products_list, 
                    qty=qty_value, 
                    partner=current_self.order_id.partner_id.id
                )
                
                price = price_data[pricelist.id]
                current_self.price_unit = price
                
            except Exception as e:
                pass 
            
        return res
