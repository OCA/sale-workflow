from odoo import fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    resource_booking_type_ids = fields.Many2many(
        comodel_name="resource.booking.type",
        relation="resource_booking_type_product_attribute_value_rel",
        readonly=True,
    )
