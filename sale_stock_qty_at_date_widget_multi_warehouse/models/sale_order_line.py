# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_at_date_per_warehouse = fields.Json(
        compute="_compute_qty_at_date_per_warehouse",
        help="Technical field feeding the Qty at Date widget with the forecasted "
        "availability of the product on every warehouse at the scheduled date.",
    )

    @api.depends(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "customer_lead",
        "order_id.commitment_date",
        "state",
        "display_qty_widget",
        "move_ids",
        "move_ids.forecast_availability",
        "qty_available_today",
        "free_qty_today",
        "virtual_available_at_date",
    )
    def _compute_qty_at_date_per_warehouse(self):
        """Read the availability of the product on every warehouse.

        The values are exposed to the ``qty_at_date_widget`` so it can decide the
        icon color (enough stock on the line's warehouse, enough stock only when
        gathering all the warehouses, or not enough stock at all) and render the
        per-warehouse breakdown in the popover.
        """
        self.qty_at_date_per_warehouse = False
        warehouses = self.env["stock.warehouse"].search(
            [("company_id", "in", self.order_id.company_id.ids)]
        )
        # Group the lines by their scheduled date to batch the product reads.
        grouped_lines = defaultdict(lambda: self.env["sale.order.line"])
        for line in self:
            if not (line.product_id and line.display_qty_widget) or not warehouses:
                continue
            scheduled_date = line.order_id.commitment_date or line._expected_date()
            grouped_lines[scheduled_date] |= line
        for scheduled_date, lines in grouped_lines.items():
            # The line's own warehouse figures are already computed by
            # ``sale_stock`` (``qty_available_today``, ``free_qty_today`` and
            # ``virtual_available_at_date``), so we reuse them below and only
            # read the availability of the remaining warehouses. This avoids a
            # redundant read and keeps the current warehouse row consistent with
            # the base widget numbers.
            qties_per_warehouse = {}
            for warehouse in warehouses:
                products = lines.filtered(
                    lambda sol, wh=warehouse: sol.warehouse_id != wh
                ).mapped("product_id")
                if not products:
                    continue
                product_qties = products.with_context(
                    to_date=scheduled_date, warehouse_id=warehouse.id
                ).read(["qty_available", "free_qty", "virtual_available"])
                qties_per_warehouse[warehouse.id] = {
                    product["id"]: product for product in product_qties
                }
            for line in lines:
                product = line.product_id
                line_uom = line.product_uom
                product_uom = product.uom_id
                convert = bool(line_uom and product_uom and line_uom != product_uom)
                breakdown = []
                for warehouse in warehouses:
                    if warehouse == line.warehouse_id:
                        # Reuse the values already computed by ``sale_stock`` for
                        # the line's own warehouse (already in the line's UoM).
                        breakdown.append(
                            {
                                "warehouse_id": warehouse.id,
                                "warehouse_name": warehouse.display_name,
                                "qty_available": line.qty_available_today,
                                "free_qty": line.free_qty_today,
                                "virtual_available": line.virtual_available_at_date,
                            }
                        )
                        continue
                    qties = qties_per_warehouse[warehouse.id][product.id]
                    qty_available = qties["qty_available"]
                    free_qty = qties["free_qty"]
                    virtual_available = qties["virtual_available"]
                    if convert:
                        qty_available = product_uom._compute_quantity(
                            qty_available, line_uom
                        )
                        free_qty = product_uom._compute_quantity(free_qty, line_uom)
                        virtual_available = product_uom._compute_quantity(
                            virtual_available, line_uom
                        )
                    breakdown.append(
                        {
                            "warehouse_id": warehouse.id,
                            "warehouse_name": warehouse.display_name,
                            "qty_available": qty_available,
                            "free_qty": free_qty,
                            "virtual_available": virtual_available,
                        }
                    )
                line.qty_at_date_per_warehouse = breakdown
