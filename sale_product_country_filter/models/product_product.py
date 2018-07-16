# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    var_blacklisted_countries_ids = fields.Many2many(
        "res.country", string="Blacklisted countries"
    )
