from odoo import fields, models


class ProductPricelist(models.Model):
    """Extend to add is_promotion_pricelist field."""

    _inherit = "product.pricelist"

    is_promotion_pricelist = fields.Boolean("Promotion Pricelist")
