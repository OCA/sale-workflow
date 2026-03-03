# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends(
        "product_variant_ids.resource_booking_type_id",
        "product_variant_ids.resource_booking_type_combination_rel_id",
    )
    def _compute_resource_booking_type_and_combination_rel(self):
        for tmpl in self:
            _type = {v.resource_booking_type_id.id for v in tmpl.product_variant_ids}
            combination = {
                v.resource_booking_type_combination_rel_id.id
                for v in tmpl.product_variant_ids
            }
            tmpl.resource_booking_type_id = _type.pop() if len(_type) == 1 else None
            tmpl.resource_booking_type_combination_rel_id = (
                combination.pop() if len(combination) == 1 else None
            )

    def _inverse_resource_booking_type_and_combination_rel(self):
        for tmpl in self:
            variants = tmpl.product_variant_ids
            variants.resource_booking_type_id = tmpl.resource_booking_type_id
            variants.resource_booking_type_combination_rel_id = (
                tmpl.resource_booking_type_combination_rel_id
            )

    resource_booking_type_id = fields.Many2one(
        "resource.booking.type",
        compute="_compute_resource_booking_type_and_combination_rel",
        inverse="_inverse_resource_booking_type_and_combination_rel",
        store=True,
    )
    resource_booking_type_combination_rel_id = fields.Many2one(
        "resource.booking.type.combination.rel",
        compute="_compute_resource_booking_type_and_combination_rel",
        inverse="_inverse_resource_booking_type_and_combination_rel",
        store=True,
    )

    def _set_resource_booking_type_id_from_variant(self):
        pass
