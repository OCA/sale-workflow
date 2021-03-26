# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductSet(models.Model):
    _inherit = 'product.set'

    # field name on sale order line: ``sale_layout_cat_id``
    section_id = fields.Many2one('sale.layout_category', string="Section",)
