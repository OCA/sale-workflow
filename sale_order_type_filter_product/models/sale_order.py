# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    type_allowed_product_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_type_allowed_product_ids",
    )

    @api.depends("type_id")
    def _compute_type_allowed_product_ids(self):
        Product = self.env["product.product"]
        for order in self:
            domain = []
            if order.type_id:
                domain = [
                    "|",
                    ("variant_sale_order_type_ids", "in", order.type_id.ids),
                    "&",
                    ("variant_sale_order_type_ids", "=", False),
                    "|",
                    ("product_tmpl_id.sale_order_type_ids", "=", False),
                    (
                        "product_tmpl_id.sale_order_type_ids",
                        "in",
                        order.type_id.ids,
                    ),
                ]
            order.type_allowed_product_ids = Product.search(domain)

    def _get_invalid_sale_order_type_lines(self, sale_order_type=None):
        self.ensure_one()
        sale_order_type = sale_order_type or self.type_id
        invalid_lines = self.env["sale.order.line"]
        for line in self.order_line.filtered(
            lambda line: line.product_id and not line.display_type
        ):
            allowed_types = line.product_id._get_allowed_sale_order_types()
            if allowed_types and sale_order_type not in allowed_types:
                invalid_lines |= line
        return invalid_lines

    def write(self, vals):
        if vals.get("type_id"):
            sale_order_type = self.env["sale.order.type"].browse(vals["type_id"])
            for order in self:
                invalid_lines = order._get_invalid_sale_order_type_lines(
                    sale_order_type=sale_order_type
                )
                if not invalid_lines:
                    continue
                action = order.company_id.sale_order_type_invalid_product_action
                if action == "prevent":
                    product_names = "\n".join(
                        f"- {line.product_id.display_name}" for line in invalid_lines
                    )
                    raise exceptions.UserError(
                        _(
                            "You cannot change the sale order type because the "
                            "following products are not allowed for the selected "
                            "type:\n%(products)s",
                            products=product_names,
                        )
                    )
                if action == "remove":
                    invalid_lines.unlink()
        return super().write(vals)
