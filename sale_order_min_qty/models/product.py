# Copyright 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    sale_min_qty = fields.Float(string='Min Sale Qty', default=1)
    force_sale_min_qty = fields.Boolean(string='Force Min Qty',
            help='If force min qty is checked, the min quantity '
                 'is only indicative value.')

