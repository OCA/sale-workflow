# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_require_commitment_date = fields.Boolean(
        compute="_compute_sale_require_commitment_date"
    )
    sale_commitment_date_in_header = fields.Boolean(
        related="company_id.sale_commitment_date_in_header"
    )

    @api.depends(
        "company_id.sale_require_commitment_date",
        "locked",
        "order_line.qty_delivered",
        "order_line.product_uom_qty",
    )
    def _compute_sale_require_commitment_date(self):
        for order in self:
            if not order.company_id.sale_require_commitment_date:
                order.sale_require_commitment_date = False
            elif order.locked:
                order.sale_require_commitment_date = False
            elif order.order_line and all(
                line.qty_delivered >= line.product_uom_qty for line in order.order_line
            ):
                order.sale_require_commitment_date = False
            else:
                order.sale_require_commitment_date = True
