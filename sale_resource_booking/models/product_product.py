import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _default_resource_booking_type_id(self):
        return self.product_tmpl_id.resource_booking_type_id

    def _default_resource_booking_type_combination_rel_id(self):
        return self.product_tmpl_id.resource_booking_type_combination_rel_id

    def _compute_resource_booking_count(self):
        for p in self:
            p.resource_booking_count = len(p.resource_booking_ids)

    resource_booking_type_id = fields.Many2one(
        "resource.booking.type",
        string="Booking type",
        index=True,
        ondelete="restrict",
        help="If set, one pending booking will be generated when sold.",
        default=lambda self: self._default_resource_booking_type_id(),
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
        default=lambda self: self._default_resource_booking_type_combination_rel_id(),
    )
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
        installed_timeline = self._is_module_installed("resource_booking_timeline")
        action["context"] = {
            "default_combination_auto_assign": False if installed_timeline else True,
            "default_product_id": self.id,
            "default_type_id": self.resource_booking_type_id.id,
        }
        # depends on partner_product_price
        if "partner_id" in self._fields:
            action["context"]["default_partner_ids"] = [self.partner_id.id]
        return action

    def create(self, vals_list):
        products = super().create(vals_list)
        products.env.cr.commit()

        # When a product has exactly one attribute,
        # then the product will inherit from product.attribute.value:
        # - resource_booking_type_id
        # - resource_booking_type_combination_rel_id
        for product in products:
            _type = {
                ptav.product_attribute_value_id.resource_booking_type_id
                for ptav in product.product_template_attribute_value_ids
            }
            if _type and len(_type) == 1:
                product.resource_booking_type_id = _type.pop().id
                _logger.debug(
                    "product.resource_booking_type_id: {}".format(
                        product.resource_booking_type_id
                    )
                )
            type_combination_rel = {
                ptav.product_attribute_value_id.resource_booking_type_combination_rel_id
                for ptav in product.product_template_attribute_value_ids
            }
            if type_combination_rel and len(type_combination_rel) == 1:
                product.resource_booking_type_combination_rel_id = (
                    type_combination_rel.pop().id
                )
                _logger.debug(
                    "p.resource_booking_type_combination_rel_id: {}".format(
                        product.resource_booking_type_combination_rel_id
                    )
                )
            product.flush_recordset()
            product.invalidate_recordset()
        return products

    def _is_module_installed(self, module_name):
        module = self.env["ir.module.module"].search([("name", "=", module_name)])
        return True if module and module.state == "installed" else False
