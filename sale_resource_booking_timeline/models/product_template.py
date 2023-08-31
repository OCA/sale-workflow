from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    resource_booking_ids = fields.Many2many(
        comodel_name="resource.booking",
        relation="product_template_resource_booking_rel",
        string="Show in Timeline",
    )
