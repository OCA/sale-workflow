# -*- encoding: utf-8 -*-
from openerp import fields, models, _


class ProductBundle(models.Model):
    _name = 'product.bundle'
    _description = 'Product bundle'

    name = fields.Char(_('Name'), help=_('Product bundle name'), required=True)
    bundle_line_ids = fields.Many2many(
        'product.bundle.line', 'product_bundle_product_bundle_line',
        'product_bundle_id', 'product_bundle_line_id', string=_('Bundle lines'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
