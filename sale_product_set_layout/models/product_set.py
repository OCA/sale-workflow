# -*- encoding: utf-8 -*-
from openerp import models, fields


class ProductSet(models.Model):
    _inherit = 'product.set'

    # field name on sale order line: ``sale_layout_cat_id``
    section_id = fields.Many2one('sale_layout.category', string=u"Section",)
