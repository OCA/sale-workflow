# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    lock_product_prices_applied_on = fields.Selection(
        string="Lock price when rule is applied on",
        selection=[
            ("3_global", "All products"),
            ("2_product_category", "Product Category"),
            ("1_product", "Product"),
            ("0_product_variant", "Product Variant"),
        ],
        help="Avoid that salesmen change prices based on this scope. Rules applied on "
        "base pricelist take into account the items of those pricelists with the rule "
        "of the pricelist applied on the sale order",
    )

    def _get_base_product_rule(self, product, quantity, uom=None, date=False, **kwargs):
        """Recurrent method to pull the pricelist item from the pricelist chain of
        inheritance"""
        self.ensure_one()
        item = self.env["product.pricelist.item"].browse(
            self._get_product_rule(product, quantity, uom, date, **kwargs)
        )
        if item.base and item.base == "pricelist" and item.base_pricelist_id:
            return item.base_pricelist_id._get_base_product_rule(
                product, quantity, uom, date, **kwargs
            )
        return item.id
