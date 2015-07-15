# -*- encoding: utf-8 -*-
from openerp import fields, models, _

import openerp.addons.decimal_precision as dp


class product_bundle(models.Model):
    _name = 'product.bundle'
    _description = 'Product bundle'

    name = fields.Char(_('Name'), help=_('Product bundle name'), required=True)
    bundle_line_ids = fields.Many2many(
        'product.bundle.line', 'product_bundle_product_bundle_line',
        'product_bundle_id', 'product_bundle_line_id', string=_('Bundle lines'))


class product_bundle_line(models.Model):
    _name = 'product.bundle.line'
    _description = 'Product bundle line'
    _rec_name = 'product_id'

    product_id = fields.Many2one(
        'product.product', domain=[('sale_ok', '=', True)], string=_('Product'), required=True)
    quantity = fields.Float(
        string=_('Quantity'), digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1)
    product_bundle_id = fields.Many2one(
        'product.bundle', _('Bundle reference'), ondelete='cascade')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
