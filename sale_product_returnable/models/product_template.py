# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class ProductTempleate(models.Model):
    _inherit = "product.template"

    returnable = fields.Boolean('Can be Returned?')
    return_product_id = fields.Many2one(
        'product.product', 'Returned Product')
