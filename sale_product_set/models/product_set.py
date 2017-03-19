# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductSet(models.Model):
    _name = 'product.set'
    _description = 'Product set'

    name = fields.Char(help='Product set name', required=True)
    set_line_ids = fields.One2many(
        comodel_name='product.set.line', inverse_name='product_set_id',
        string='Products')
