# Copyright 2020 Akretion Renato Lima <renato.lima@akretion.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="BoM",
        domain="[('product_tmpl_id.product_variant_ids', '=', product_id),"
        "'|', ('product_id', '=', product_id), "
        "('product_id', '=', False)]",
    )

    @api.constrains("bom_id", "product_id")
    def _check_match_product_variant_ids(self):
        for line in self:
            if not line.bom_id:
                continue
            bom_product = line.bom_id.product_id
            bom_product_tmpl = line.bom_id.product_tmpl_id

            if bom_product and bom_product == line.product_id:
                continue
            if not bom_product and bom_product_tmpl == line.product_template_id:
                continue
            raise ValidationError(
                _(
                    "Please select a BoM that matches the product %(product)s",
                    product=line.product_id.display_name,
                )
            )
