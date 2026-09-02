# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    sale_multiple_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Sales Multiple",
        help="When set, sale order quantities are rounded up to an "
        "multiple number of this unit.",
    )
