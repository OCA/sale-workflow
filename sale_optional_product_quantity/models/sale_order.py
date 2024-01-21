# Copyright 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _update_product_uom_qty(self):
        """
        Update lines quantity based on optional product
        quantities configured in product templates
        from other lines of this Quotation/Sale Order.
        """
        for order in self:
            for line in order.order_line:
                line = line.with_context(**{"product_uom_qty.loop_safe": False})
                line_product_id = line.product_id.product_tmpl_id.id
                order_lines = order.order_line.filtered(
                    lambda x: line_product_id
                    in (x.product_template_id.optional_product_ids.ids)
                )
                if not order_lines:
                    line.product_uom_qty = line.product_uom_qty or 1.0
                    continue

                multiplier = sum(
                    order_lines.mapped("product_template_id")
                    .mapped("product_optional_line_ids")
                    .mapped("quantity")
                )
                qty = sum(order_lines.mapped("product_uom_qty"))
                line.product_uom_qty = (qty * multiplier) or 1.0
