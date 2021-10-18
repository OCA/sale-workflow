# Copyright 2020 Tecnactiva - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    secondary_uom_factor = fields.Float(
        related="secondary_uom_id.factor", store=False, readonly=True
    )
    secondary_uom_rounding = fields.Float(
        related="secondary_uom_id.uom_id.rounding", store=False, readonly=True
    )
    secondary_uom_product_variant_ids = fields.One2many(
        related="secondary_uom_id.product_tmpl_id.product_variant_ids",
        store=False,
        readonly=True,
    )
