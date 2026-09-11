# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_sale_order_type_ids = fields.Many2many(
        comodel_name="sale.order.type",
        relation="product_product_sale_order_type_rel",
        column1="product_id",
        column2="sale_order_type_id",
        string="Variant Sale Order Types",
        help="Sale order types for which this product variant is allowed.",
    )

    def _get_allowed_sale_order_types(self):
        """Return the sale order types allowed for this product variant."""
        self.ensure_one()
        # Use sudo to read types from other companies, as they are needed to
        # determine whether the product variant is restricted.
        product = self.sudo()
        sale_order_types = product.variant_sale_order_type_ids
        if not sale_order_types:
            sale_order_types = product.product_tmpl_id.sale_order_type_ids
        return sale_order_types
