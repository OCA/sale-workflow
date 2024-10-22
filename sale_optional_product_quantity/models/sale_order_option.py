# Copyright 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleOrderOption(models.Model):
    _inherit = "sale.order.option"

    quantity = fields.Float(
        compute="_compute_quantity",
        readonly=False,
        store=True,
    )

    @api.depends(
        "order_id.order_line",
        "order_id.order_line.product_template_id",
        "order_id.order_line.product_uom_qty",
    )
    def _compute_quantity(self):
        """
        Compute quantity based on optional product
        quantities configured in product templates
        from lines of Quotation/Sale Order.
        """
        optional_quantity_enabled = self.env.user.has_group(
            "product_optional_product_quantity.group_product_optional_quantity"
        )
        if not optional_quantity_enabled:
            for option in self:
                option.quantity = option.quantity
            return
        for option in self:
            order = option.order_id
            option_product_id = option.product_id.product_tmpl_id.id
            order_lines = order.order_line.filtered(
                lambda x: option_product_id
                in (x.product_template_id.optional_product_ids.ids)
            )
            if not order_lines:
                option.quantity = 1
                continue

            multiplier = sum(
                order_lines.mapped("product_template_id")
                .mapped("product_optional_line_ids")
                .filtered(lambda x: x.optional_product_tmpl_id.id == option_product_id)
                .mapped("quantity")
            )
            qty = sum(order_lines.mapped("product_uom_qty"))
            option.quantity = qty * multiplier
