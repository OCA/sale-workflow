# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    fixed_price_no_discount = fields.Boolean(
        string="Prevent Discounts on Fixed Price",
        default=True,
        help=(
            "Prevent manual discounts on sale order lines when this fixed-price "
            "rule is applied."
        ),
    )

    def _has_fixed_price_no_discount(self, product, quantity, uom, date, visited=None):
        if not self:
            return False
        self.ensure_one()
        if self.compute_price == "fixed":
            return self.fixed_price_no_discount
        if self.base != "pricelist" or not self.base_pricelist_id:
            return False

        visited = visited or self.browse()
        if self in visited:
            return False
        rule_id = self.base_pricelist_id._get_product_rule(
            product, quantity=quantity, uom=uom, date=date
        )
        return self.browse(rule_id)._has_fixed_price_no_discount(
            product, quantity=quantity, uom=uom, date=date, visited=visited | self
        )
