import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends(
        "product_variant_ids.resource_booking_type_id",
        "product_variant_ids.resource_booking_type_combination_rel_id",
    )
    def _compute_resource_booking_type(self):
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

    def _inverse_resource_booking_type(self):
        for tmpl in self:
            variants = tmpl.product_variant_ids
            variants.resource_booking_type_id = tmpl.resource_booking_type_id
            variants.resource_booking_type_combination_rel_id = (
                tmpl.resource_booking_type_combination_rel_id
            )

    resource_booking_type_id = fields.Many2one(
        "resource.booking.type",
        compute="_compute_resource_booking_type",
        inverse="_inverse_resource_booking_type",
        store=False,
    )
    resource_booking_type_combination_rel_id = fields.Many2one(
        "resource.booking.type.combination.rel",
        compute="_compute_resource_booking_type",
        inverse="_inverse_resource_booking_type",
        store=False,
    )
