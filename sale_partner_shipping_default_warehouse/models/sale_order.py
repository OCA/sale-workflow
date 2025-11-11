# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("user_id", "company_id", "partner_shipping_id")
    def _compute_warehouse_id(self):
        orders = self.filtered(
            lambda o: o.partner_shipping_id.default_sale_warehouse_id
        )
        for order in orders:
            order.warehouse_id = order.partner_shipping_id.default_sale_warehouse_id
        return super(SaleOrder, self - orders)._compute_warehouse_id()
