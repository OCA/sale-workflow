# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    """Add a direct view on applied tiered pricing items for quick view/edit.
    """

    _inherit = "product.product"

    tiered_pricing_items = fields.Many2many(
        "product.pricelist.item",
        compute="_compute_tiered_pricing_items",
        help="Tiered Pricing items",
    )

    def _compute_tiered_pricing_items(self):
        tiered_domain = [
            ("applied_on", "=", "0_product_variant"),
            ("product_id", "in", self.ids),
        ]
        tiered_items = self.env["product.pricelist.item"].search(tiered_domain)
        for product in self:
            ptis = tiered_items.filtered(lambda i, j=product: i.product_id == j)
            product.tiered_pricing_items = ptis.mapped("tiered_pricelist_id.tier_items")
