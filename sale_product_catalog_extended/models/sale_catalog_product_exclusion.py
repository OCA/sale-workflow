# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleCatalogProductExclusion(models.Model):
    _name = "sale.catalog.product.exclusion"
    _description = "Product excluded from the catalog last sales origin"
    _rec_name = "product_id"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
        ondelete="cascade",
        index=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
        ondelete="cascade",
        index=True,
    )

    _sql_constraints = [
        (
            "partner_product_uniq",
            "unique(partner_id, product_id)",
            "This product is already excluded from the last sales of this partner.",
        ),
    ]
