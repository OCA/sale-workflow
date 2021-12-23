from odoo import fields, models


class ProductSet(models.Model):
    _inherit = "product.set.line"

    product_id = fields.Many2one(required=False)
    display_type = fields.Selection(
        [
            ("line_section", "Section"),
            ("line_note", "Note"),
        ]
    )
    name = fields.Char()
