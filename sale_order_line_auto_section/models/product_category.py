# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"
    _order = "section_sequence,name"

    section_sequence = fields.Integer(
        default=10,
        help="Sequence order when creating sale order sections by category. "
        "Lower values appear first.",
    )
    section_title = fields.Char(
        help="Title to use when creating sale order sections for this category. "
        "If empty, the category name will be used.",
        translate=True,
    )
    section_sort_by = fields.Selection(
        [
            ("sequence", "Manual Order"),
            ("default_code", "Internal Reference"),
        ],
        string="Sort Lines By",
        default="sequence",
        help="How to sort lines within this section when organizing by category",
    )
