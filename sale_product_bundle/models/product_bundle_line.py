# -*- coding: utf-8 -*-
from openerp import fields, models, _

import openerp.addons.decimal_precision as dp


class ProductBundleLine(models.Model):
    _name = 'product.bundle.line'
    _description = 'Product bundle line'
    _rec_name = 'product_id'
    _order = 'sequence'

    product_id = fields.Many2one(
        'product.product', domain=[('sale_ok', '=', True)],
        string=_('Product'), required=True)
    quantity = fields.Float(
        string=_('Quantity'),
        digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1)
    product_bundle_id = fields.Many2one(
        'product.bundle', _('Bundle reference'), ondelete='cascade')
    sequence = fields.Integer(
        string=_('Sequence'),
        required=True, default=0,
        help=_(u""),
    )
