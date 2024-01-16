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

    @api.depends("order_id.order_line")
    def _compute_quantity(self):
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
                .mapped("quantity")
            )
            qty = sum(order_lines.mapped("product_uom_qty"))
            option.quantity = qty * multiplier
