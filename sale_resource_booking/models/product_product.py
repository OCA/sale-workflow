from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_resource_booking_count(self):
        for p in self:
            p.resource_booking_count = len(p.resource_booking_ids)

    resource_booking_count = fields.Integer(
        compute="_compute_resource_booking_count",
        string="Booking Count",
    )
    resource_booking_ids = fields.One2many(
        "resource.booking",
        "product_id",
        string="Bookings",
    )

    def action_view_resource_booking(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "resource_booking.resource_booking_action"
        )
        action["context"] = {
            "default_product_id": self.id,
            "default_type_id": self.resource_booking_type_id.id,
        }
        try:
            # depends on partner_product_price
            action["context"]["default_partner_id"] = self.partner_id.id
        except:
            pass
        return action
