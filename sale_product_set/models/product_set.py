# -*- coding: utf-8 -*-
# Copyright 2015 Anybox S.A.S
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductSet(models.Model):
    _name = 'product.set'
    _description = 'Product set'

    name = fields.Char(
        string='Name',
        help='Product set name',
        required=True
    )
    set_line_ids = fields.One2many(
        'product.set.line',
        'product_set_id',
        string="Products"
    )
