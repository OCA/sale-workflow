from odoo import fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    resource_booking_type_id = fields.Many2one(
        "resource.booking.type",
        string="Booking type",
        index=True,
        ondelete="restrict",
        help="If set, one pending booking will be generated when sold.",
    )
    resource_booking_type_combination_rel_id = fields.Many2one(
        "resource.booking.type.combination.rel",
        string="Resource combination",
        index=True,
        ondelete="restrict",
        domain="[('type_id', '=', resource_booking_type_id)]",
        help=(
            "If set, the booking will be created with this resource combination. "
            "Otherwise, the combination will be assigned automatically later, "
            "when the requester schedules the booking."
        ),
    )

    def write(self, vals):
        super().write(vals)
        # Update product variants
        product_vals = {}
        if "resource_booking_type_id" in vals:
            product_vals["resource_booking_type_id"] = vals["resource_booking_type_id"]
            product_vals["resource_booking_type_combination_rel_id"] = None
        if "resource_booking_type_combination_rel_id" in vals:
            product_vals["resource_booking_type_combination_rel_id"] = vals[
                "resource_booking_type_combination_rel_id"
            ]
        if product_vals:
            ptavs = self.env["product.template.attribute.value"].search(
                [("product_attribute_value_id", "in", self.ids)]
            )
            products = ptavs.mapped("ptav_product_variant_ids")
            products.write(product_vals)
        return
