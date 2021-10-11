from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    primeship_activation = fields.Boolean(string="Activates primeship", default=False)
    primeship_duration = fields.Integer(
        string="Primeship duration (in months)", default=12
    )
