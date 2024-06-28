from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Catalog related fields
    product_catalog_product_previously_sold = fields.Boolean(
        compute="_compute_product_catalog_product_previously_sold",
        search="_search_product_catalog_product_previously_sold",
    )

    @api.depends_context("order_id")
    def _compute_product_catalog_product_previously_sold(self):
        order_id = self.env.context.get("order_id")
        if not order_id:
            self.product_catalog_product_previously_sold = False
            return
        order = self.env["sale.order"].browse(order_id)
        read_group_data = self.env["sale.order.line"]._read_group(
            domain=[("order_id.partner_id", "=", order.partner_id.id)],
            groupby=["product_id"],
            aggregates=["__count"],
        )
        data = {product.id: count for product, count in read_group_data}
        for product in self:
            product.product_catalog_product_previously_sold = bool(
                data.get(product.id, 0)
            )

    def _search_product_catalog_product_previously_sold(self, operator, value):
        if operator not in ["=", "!="] or not isinstance(value, bool):
            raise UserError(_("Operation not supported"))
        order_id = self.env.context.get("order_id", "")
        order = self.env["sale.order"].browse(order_id)
        product_ids = (
            self.env["sale.order.line"]
            .search(
                [
                    ("order_id.partner_id", "in", [order.partner_id.id]),
                ]
            )
            .product_id.ids
        )
        return [("id", "in", product_ids)]
