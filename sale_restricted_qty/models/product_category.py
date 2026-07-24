# Copyright 2019 Akretion
# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "sale.product.restricted.qty.mixin"]

    _sale_restricted_qty_parent_field = "parent_id"
