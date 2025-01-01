# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    warehouse_id = fields.Many2one(
        compute="_compute_warehouse_id", store=True, precompute=True
    )

    @api.depends("partner_id")
    def _compute_warehouse_id(self):
        sales_with_partner_warehouse = self.filtered(
            lambda sale: sale.state == "draft" and sale.partner_id.sale_warehouse_id
        )
        for sale in sales_with_partner_warehouse:
            sale.warehouse_id = sale.partner_id.sale_warehouse_id
        return super(
            SaleOrder, self - sales_with_partner_warehouse
        )._compute_warehouse_id()
