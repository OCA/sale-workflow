import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _default_resource_booking_type_id(self):
        if self.product_tmpl_id:
            return self.product_tmpl_id.resource_booking_type_id
        return False

    def _default_resource_booking_type_combination_rel_id(self):
        if self.product_tmpl_id:
            return self.product_tmpl_id.resource_booking_type_combination_rel_id
        return False

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

    @api.model_create_multi
    def create(self, vals_list):
        products = super(ProductProduct, self).create(vals_list)
        for prod, vals in zip(products, vals_list):
            if "resource_booking_type_id" in vals:
                pass
            elif "product_template_attribute_value_ids" in vals:
                prod._set_resource_booking_type_id_from_pav_if_empty()
        return products

    def write(self, vals):
        super(ProductProduct, self).write(vals)
        if "resource_booking_type_id" in vals:
            pass
        elif "product_template_attribute_value_ids" in vals:
            self._set_resource_booking_type_id_from_pav_if_empty()
        return True

    def _set_resource_booking_type_id_from_pav_if_empty(self):
        """
        Get booking types matching the product's attribute values.
        If there is exactly one booking type, return it.
        """
        if self.resource_booking_type_id:
            return
        pav = self.product_template_attribute_value_ids.product_attribute_value_id
        if pav:
            booking_type = (
                self.env["resource.booking.type"]
                .search([("product_attribute_value_ids", "in", pav.ids)])
                .filtered(
                    lambda t: len(t.product_attribute_value_ids) == len(pav.ids)
                    and set(t.product_attribute_value_ids.ids) == set(pav.ids)
                )
            )
            if booking_type and len(booking_type) == 1:
                self.resource_booking_type_id = booking_type.id

    def _is_module_installed(self, module_name):
        module = self.env["ir.module.module"].search([("name", "=", module_name)])
        return True if module and module.state == "installed" else False
