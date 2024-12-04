# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    stock_per_warehouse_info = fields.Html(
        string="Stock / Warehouse", compute="_compute_stock_per_warehouse_info"
    )

    @api.depends("product_id")
    def _compute_stock_per_warehouse_info(self):
        for line in self:
            info = ""
            if line.product_id:
                warehouses = self.env["stock.warehouse"].search(
                    [
                        ("company_id", "=", line.order_id.company_id.id),
                        ("display_stock_on_sol", "=", True),
                    ]
                )
                for warehouse in warehouses:
                    qty_available = line.product_id.with_context(
                        warehouse=warehouse.id
                    ).qty_available
                    info += f"<span>{warehouse.code}: {qty_available}</span><br/>"
            line.stock_per_warehouse_info = info
