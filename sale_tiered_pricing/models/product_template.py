# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    """Add a direct view on applied tiered pricing items for quick view/edit.
    """

    _inherit = "product.template"

    tiered_pricing_items = fields.Many2many(
        "product.pricelist.item",
        compute="_compute_tiered_pricing_items",
        help="Tiered Pricing items",
    )

    def _compute_tiered_pricing_items(self):
        tiered_domain = [
            ("applied_on", "=", "1_product"),
            ("product_tmpl_id", "in", self.ids),
        ]
        tiered_items = self.env["product.pricelist.item"].search(tiered_domain)
        for tmpl in self:
            ttis = tiered_items.filtered(lambda i, j=tmpl: i.product_tmpl_id == j)
            tmpl.tiered_pricing_items = ttis.mapped("tiered_pricelist_id.tier_items")
