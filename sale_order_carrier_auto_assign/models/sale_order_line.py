# Copyright 2020 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        order_lines = super().create(vals_list)
        order_lines.order_id._auto_set_carrier_on_create()
        return order_lines

    def write(self, vals):
        # When product is changed, set the carrier
        res = super().write(vals)
        if vals.get("product_id"):
            # compute of is_all_service doesn't list order_line.product_id in its
            # depends, so invalidate recordset
            self.order_id.invalidate_recordset(["is_all_service"])
            self.order_id._auto_set_carrier_on_create()
        return res
