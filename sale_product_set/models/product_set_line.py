# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models

import openerp.addons.decimal_precision as dp


class ProductSetLine(models.Model):
    _name = 'product.set.line'
    _description = 'Product set line'
    _rec_name = 'product_id'
    _order = 'sequence'

    product_id = fields.Many2one(
        'product.product', domain=[('sale_ok', '=', True)],
        string='Product', required=True)
    quantity = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1)
    product_set_id = fields.Many2one(
        'product.set', string='Set', readonly=True, ondelete='cascade',
        index=True, copy=False)
    sequence = fields.Integer(required=True, default=0)
