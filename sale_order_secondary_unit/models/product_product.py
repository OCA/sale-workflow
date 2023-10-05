# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    sale_secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Default secondary unit for sales",
        help="In order to set a value, please first add at least one record"
        " in 'Secondary Unit of Measure'",
        domain="['|', ('product_id', '=', id),"
        "'&', ('product_tmpl_id', '=', product_tmpl_id),"
        "     ('product_id', '=', False)]",
    )
