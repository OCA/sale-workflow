from odoo import fields, models


class ResourceBooking(models.Model):
    _inherit = "resource.booking"

    product_template_ids = fields.Many2many(
        comodel_name="product.template",
        relation="product_template_resource_booking_rel",
        string="Show in Timeline",
    )
