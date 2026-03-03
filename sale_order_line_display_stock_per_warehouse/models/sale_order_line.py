# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    stock_per_warehouse_info = fields.Html(
        string="Stock / Warehouse", compute="_compute_stock_per_warehouse_info"
    )

    def _get_display_stock_qty(self, product, warehouse, stock_field):
        return product.with_context(warehouse_id=warehouse.id)[stock_field]

    @api.depends("product_id")
    def _compute_stock_per_warehouse_info(self):
        stock_field = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_line_stock_info.stock_field_on_sol", "qty_available")
        )
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
                    qty = line._get_display_stock_qty(
                        line.product_id, warehouse, stock_field
                    )
                    info += f"<span>{warehouse.code}: {qty}</span><br/>"
            line.stock_per_warehouse_info = info
