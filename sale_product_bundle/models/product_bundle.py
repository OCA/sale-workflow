# -*- encoding: utf-8 -*-
from openerp import fields, models, _


class ProductBundle(models.Model):
    _name = 'product.bundle'
    _description = 'Product bundle'

    name = fields.Char(_('Name'), help=_('Product bundle name'), required=True)
    bundle_line_ids = fields.One2many(
        'product.bundle.line', 'product_bundle_id', _(u"Products"))
