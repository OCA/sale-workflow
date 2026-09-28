# © 2025 OBS Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    byproduct_note_template = fields.Char(
        string="By-product Note Template",
        help="Template for the note on sale order lines created for by-products. "
        "You can use placeholders like {product_name} and {mo_name}.",
    )
