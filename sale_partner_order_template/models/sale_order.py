# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("partner_id")
    def _compute_sale_order_template_id(self):
        res = super()._compute_sale_order_template_id()
        for order in self:
            if order.partner_id.sale_order_template_id:
                order.sale_order_template_id = order.partner_id.sale_order_template_id
        return res
