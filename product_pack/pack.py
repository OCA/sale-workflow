# -*- encoding: latin-1 -*-
from openerp import fields, models


class product_pack(models.Model):
    _name = 'product.pack.line'
    _rec_name = 'product_id'

    parent_product_id = fields.Many2one(
        'product.product', 'Parent Product',
        ondelete='cascade', required=True)
    quantity = fields.Float(
        'Quantity', required=True)
    product_id = fields.Many2one(
        'product.product', 'Product', required=True)


class product_product(models.Model):
    _inherit = 'product.product'

    pack_line_ids = fields.One2many(
        'product.pack.line', 'parent_product_id', 'Pack Products',
        help='List of products that are part of this pack.')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
