# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResourceBookingType(models.Model):
    _inherit = "resource.booking.type"

    product_ids = fields.One2many(
        comodel_name="product.product",
        inverse_name="resource_booking_type_id",
        string="Products",
    )

    def action_sale_order_wizard(self):
        """Help user creating a sale order for this RBT."""
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_resource_booking.resource_booking_sale_action"
        )
        result["context"] = dict(self.env.context, default_type_id=self.id)
        return result
