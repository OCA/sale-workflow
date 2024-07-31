# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResourceBookingType(models.Model):
    _inherit = "resource.booking.type"

    product_ids = fields.One2many(
        comodel_name="product.product",
        inverse_name="resource_booking_type_id",
        string="Products",
    )
    product_attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        relation="resource_booking_type_product_attribute_value_rel",
        help="The booking type will be set on "
        "new product variants which have "
        "this combination of attribute values. "
        "The combination must be unique per booking type.",
    )

    @api.constrains("product_attribute_value_ids")
    def _check_unique_product_attribute_value_ids(self):
        # Assuming that existing records have unique product.attribute.value combination
        combinations = {
            frozenset(r.product_attribute_value_ids.ids): r
            for r in self.search([("id", "not in", self.ids)])
        }
        for record in self:
            combination = frozenset(record.product_attribute_value_ids.ids)
            if combination and combination in combinations:
                raise ValidationError(
                    _("{} has the same combination of Attribute Values.").format(
                        combinations[combination].name
                    )
                )
            combinations[combination] = record

    def action_sale_order_wizard(self):
        """Help user creating a sale order for this RBT."""
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_resource_booking.resource_booking_sale_action"
        )
        result["context"] = dict(self.env.context, default_type_id=self.id)
        return result
