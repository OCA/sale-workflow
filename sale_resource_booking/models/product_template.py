# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    resource_booking_type_id = fields.Many2one(
        "resource.booking.type",
        string="Booking type",
        compute="_compute_resource_booking_type_id",
        inverse="_inverse_resource_booking_type_id",
        search="_search_resource_booking_type_id",
        ondelete="restrict",
        help="If set, one pending booking will be generated when sold.",
    )
    resource_booking_type_combination_rel_id = fields.Many2one(
        "resource.booking.type.combination.rel",
        string="Resource combination",
        compute="_compute_resource_booking_type_combination_rel_id",
        inverse="_inverse_resource_booking_type_combination_rel_id",
        search="_search_resource_booking_type_combination_rel_id",
        domain="[('type_id', '=', resource_booking_type_id)]",
        ondelete="restrict",
        help=(
            "If set, the booking will be created with this resource combination. "
            "Otherwise, the combination will be assigned automatically later, "
            "when the requester schedules the booking."
        ),
    )

    def _get_related_fields_variant_template(self):
        res = super()._get_related_fields_variant_template()
        return res + [
            "resource_booking_type_id",
            "resource_booking_type_combination_rel_id",
        ]

    @api.depends("product_variant_ids.resource_booking_type_id")
    def _compute_resource_booking_type_id(self):
        self._compute_template_field_from_variant_field("resource_booking_type_id")

    def _inverse_resource_booking_type_id(self):
        self._set_product_variant_field("resource_booking_type_id")

    def _search_resource_booking_type_id(self, operator, value):
        return [("product_variant_ids.resource_booking_type_id", operator, value)]

    @api.depends("product_variant_ids.resource_booking_type_combination_rel_id")
    def _compute_resource_booking_type_combination_rel_id(self):
        self._compute_template_field_from_variant_field(
            "resource_booking_type_combination_rel_id"
        )

    def _inverse_resource_booking_type_combination_rel_id(self):
        self._set_product_variant_field("resource_booking_type_combination_rel_id")

    def _search_resource_booking_type_combination_rel_id(self, operator, value):
        return [
            (
                "product_variant_ids.resource_booking_type_combination_rel_id",
                operator,
                value,
            )
        ]
