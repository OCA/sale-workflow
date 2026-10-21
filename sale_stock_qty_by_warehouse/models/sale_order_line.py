# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    display_qty_by_warehouse_widget = fields.Boolean(
        compute="_compute_display_qty_by_warehouse_widget",
    )
    qty_by_warehouse_widget_data = fields.Binary(
        compute="_compute_qty_by_warehouse_widget_data"
    )

    @api.depends("product_id")
    def _compute_display_qty_by_warehouse_widget(self):
        for rec in self:
            product = rec.product_id
            rec.display_qty_by_warehouse_widget = (
                product.type == "consu" and product.is_storable
            )

    @api.depends("product_id")
    def _compute_qty_by_warehouse_widget_data(self):
        warehouses = self.env["stock.warehouse"].search([])  # pylint: disable=no-search-all
        locations = warehouses.mapped("lot_stock_id")
        products = self.filtered(
            lambda sol: sol.display_qty_by_warehouse_widget
        ).mapped("product_id")
        data_by_product_id = self._get_locations_stock_qty_by_warehouse(
            locations, products
        )
        for rec in self:
            if not rec.display_qty_by_warehouse_widget:
                rec.qty_by_warehouse_widget_data = []
                continue
            rec.qty_by_warehouse_widget_data = data_by_product_id.get(rec.product_id.id)

    def _get_locations_stock_qty_by_warehouse(self, locations, products):
        data_by_product_id = defaultdict(dict)
        for location in locations:
            location_data_by_product_id = self._get_location_stock_qty_by_warehouse(
                location, products
            )
            for product_id, data in location_data_by_product_id.items():
                data_by_product_id[product_id].update(data)
        return data_by_product_id

    def _get_location_stock_qty_by_warehouse(self, location, products):
        data_by_product_id = defaultdict(dict)
        qties = products.with_context(location=location.id).read(
            ["qty_available"], load="_classic_read"
        )
        for qty_row in qties:
            product_id = qty_row.get("id")
            self._format_stock_qty_by_warehouse_row(location, qty_row)
            data_by_product_id[product_id][location.id] = qty_row
        return data_by_product_id

    def _format_stock_qty_by_warehouse_row(self, location, qty_row):
        qty_row.update(
            {
                "location_name": location.display_name,
                "warehouse_name": location.warehouse_id.name,
            }
        )
        qty_row["location_name"] = location.display_name
        return qty_row
