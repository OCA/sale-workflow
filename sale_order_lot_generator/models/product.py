# coding: utf-8
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    auto_generate_prodlot = fields.Boolean(
        string="Lot Generation Auto",
        help="Forces to specifiy a Serial Number for all "
        "lines containing this product since the confirmation "
        "of the Sale Order",
    )
