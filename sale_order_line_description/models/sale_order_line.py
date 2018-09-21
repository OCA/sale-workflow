# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if not self.user_has_groups(
                'sale_order_line_description.'
                'group_use_product_description_per_so_line'):
            return res

        if self.product_id:            
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang)
            self.name = (product.description_sale or self.name)
        return res
