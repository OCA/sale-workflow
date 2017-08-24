# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductPriceCategory(models.Model):
    _name = 'product.price.category'
    name = fields.Char(required=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price_category_id = fields.Many2one(
        'product.price.category',
        string='Price Category',
        ondelete='restrict',
    )
