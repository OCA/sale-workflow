# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderRecommendation(models.TransientModel):
    _inherit = "sale.order.recommendation"

    def _prepare_recommendation_line_vals(self, group_line, so_line=False):
        vals = super()._prepare_recommendation_line_vals(group_line, so_line=so_line)
        if so_line:
            vals["secondary_uom_id"] = so_line.secondary_uom_id.id
            vals["secondary_uom_qty"] = so_line.secondary_uom_qty
        if not vals.get("secondary_uom_id"):
            # Take default secondary unit from product if exists
            product = self.env["product.product"].browse(vals["product_id"])
            if product.sale_secondary_uom_id:
                vals["secondary_uom_id"] = product.sale_secondary_uom_id.id
        return vals
