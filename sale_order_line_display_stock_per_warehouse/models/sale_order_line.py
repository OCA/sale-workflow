# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    display_qty_per_warehouse_widget = fields.Boolean(
        compute="_compute_display_qty_per_warehouse_widget",
    )
    qty_per_warehouse_widget_data = fields.Binary(
        compute="_compute_qty_per_warehouse_widget_data",
    )

    @api.depends("product_id")
    def _compute_display_qty_per_warehouse_widget(self):
        for line in self:
            product = line.product_id
            line.display_qty_per_warehouse_widget = (
                product.type == "consu" and product.is_storable
            )

    @api.depends("product_id", "order_id.company_id")
    def _compute_qty_per_warehouse_widget_data(self):
        stock_field = self._get_qty_per_warehouse_stock_field()
        lines_by_company = defaultdict(lambda: self.browse())
        for line in self:
            lines_by_company[line.order_id.company_id] |= line

        for company, lines in lines_by_company.items():
            warehouses = lines._get_qty_per_warehouse_warehouses(company)
            products = lines.filtered("display_qty_per_warehouse_widget").product_id
            data_by_product = lines._get_products_qty_per_warehouse(
                products, warehouses, stock_field
            )
            for line in lines:
                line.qty_per_warehouse_widget_data = (
                    data_by_product.get(line.product_id.id, [])
                    if line.display_qty_per_warehouse_widget
                    else []
                )

    def _get_qty_per_warehouse_stock_field(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_line_stock_info.stock_field_on_sol", "qty_available")
        )

    def _get_qty_per_warehouse_warehouses(self, company):
        return self.env["stock.warehouse"].search(
            [
                ("company_id", "=", company.id),
                ("display_stock_on_sol", "=", True),
            ]
        )

    def _get_qty_per_warehouse_context(self, warehouse):
        locations = warehouse.display_stock_location_ids
        if locations:
            return {"location": locations.ids}
        return {"warehouse_id": warehouse.id}

    def _get_products_qty_per_warehouse(self, products, warehouses, stock_field):
        data_by_product = defaultdict(dict)
        for warehouse in warehouses:
            ctx = self._get_qty_per_warehouse_context(warehouse)
            quantities = products.with_context(**ctx).read(
                [stock_field], load="_classic_read"
            )
            for qty_row in quantities:
                data_by_product[qty_row["id"]][warehouse.id] = {
                    "warehouse_name": warehouse.display_name,
                    "qty": qty_row[stock_field],
                }
        return data_by_product
