# Copyright 2020 Tecnactiva - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    uom_category_id = fields.Many2one(related="uom_id.category_id", store=False, readonly=True)
