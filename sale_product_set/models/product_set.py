# -*- encoding: utf-8 -*-
from openerp import fields, models, _


class ProductSet(models.Model):
    _name = 'product.set'
    _description = 'Product set'

    name = fields.Char(_('Name'), help=_('Product set name'), required=True)
    set_line_ids = fields.One2many(
        'product.set.line', 'product_set_id', _(u"Products"))
