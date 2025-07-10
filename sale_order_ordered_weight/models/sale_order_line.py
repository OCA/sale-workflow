# Copyright 2021 Manuel Calero Solís (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    total_ordered_weight = fields.Float(
        compute="_compute_total_ordered_weight",
        string="Ordered Weight",
        store=True,
    )

    @api.depends(
        "product_id.weight", "product_id.uom_id", "product_uom", "product_uom_qty"
    )
    def _compute_total_ordered_weight(self):
        for line in self:
            if line.product_id:
                line.total_ordered_weight = line.product_uom._compute_quantity(
                    line.product_id.weight * line.product_uom_qty,
                    line.product_id.uom_id,
                    round=False,
                    raise_if_failure=False,
                )
            else:
                line.total_ordered_weight = 0.0
