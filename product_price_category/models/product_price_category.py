# Copyright 2016 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductPriceCategory(models.Model):
    _name = "product.price.category"
    _description = "Product Price Category"

    name = fields.Char(required=True)
