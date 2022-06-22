# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProductBrand(models.Model):
    _inherit = "product.brand"

    sale_order_mixed = fields.Boolean(
        help="Whether a sale order can contain products from different brands"
    )
