# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_multiple_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Sales Multiple",
        compute="_compute_sale_multiple_uom_id",
        inverse="_inverse_sale_multiple_uom_id",
        store=True,
        help="When set, sale order quantities are rounded up to an "
        "multiple number of this unit.",
    )

    @api.depends("product_variant_ids", "product_variant_ids.sale_multiple_uom_id")
    def _compute_sale_multiple_uom_id(self):
        self._compute_template_field_from_variant_field("sale_multiple_uom_id")

    def _inverse_sale_multiple_uom_id(self):
        self._set_product_variant_field("sale_multiple_uom_id")
