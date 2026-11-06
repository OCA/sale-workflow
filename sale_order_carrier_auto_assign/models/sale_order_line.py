# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        # When product lines are added, set the carrier
        ctx_carrier_on_create = self.env.context.get("carrier_on_create")
        order_lines = super(
            SaleOrderLine, self.with_context(carrier_on_create=True)
        ).create(vals_list)
        order_lines = order_lines.with_context(carrier_on_create=ctx_carrier_on_create)
        order_lines.order_id._set_carrier_on_create()
        return order_lines

    def write(self, vals):
        # When product is changed, set the carrier
        res = super(SaleOrderLine, self.with_context(carrier_on_create=True)).write(
            vals
        )
        if vals.get("product_id"):
            # compute of is_all_service doesn't list order_line.product_id in its
            # depends, so invalidate recordset
            self.order_id.invalidate_recordset(["is_all_service"])
            self.order_id._set_carrier_on_create()
        return res
