# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    section_id = fields.Many2one('sale_layout.category', string=u"Section",)


