# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductPricelistItem(models.Model):
    """Add the new tiered pricing way to compute_price,
       based on a is_tiered_pricing pricelist.
    """

    _inherit = "product.pricelist.item"

    compute_price = fields.Selection(selection_add=[("tier", "Tiered pricing")])
    tiered_pricelist_id = fields.Many2one(
        "product.pricelist",
        domain="[('is_tiered_pricing', '!=', False)]",
        help="In case of tiered pricing, the pricing that will be used.",
    )

    @api.constrains("compute_price")
    def _constrains_tier_items(self):
        tier_items = self.filtered(lambda i: i.compute_price == "tier")
        bad_tier_items = tier_items.filtered(
            lambda i: not i.tiered_pricelist_id.is_tiered_pricing
        )
        if bad_tier_items:
            message = _("Tiered pricings should be set on all tiered items.")
            raise ValidationError(message)

    def _get_pricelist_item_name_price(self):
        super(ProductPricelistItem, self)._get_pricelist_item_name_price()
        for item in self.filtered(lambda i: i.compute_price == "tier"):
            item.price = item.tiered_pricelist_id.name

    def _compute_price(self, price, price_uom, product, quantity=1.0, partner=False):
        if self.compute_price == "tier":
            quantity = quantity or 1  # degenerate case: we display the price for 1 unit
            qps = self.tiered_pricelist_id.get_quantities_and_prices(
                price, price_uom, product, quantity
            )  # the unit price is the weighted average
            price = sum(q * p for q, p in qps) / quantity
            return product.uom_id._compute_price(price, price_uom)

        return super(ProductPricelistItem, self)._compute_price(
            price, price_uom, product, quantity, partner
        )
