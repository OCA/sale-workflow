// Copyright 2026 Tecnativa - Carlos Roca
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import {QtyAtDateWidget} from "@sale_stock/widgets/qty_at_date_widget";

import {patch} from "@web/core/utils/patch";

function warehouseQty(data, warehouse) {
    if (data.state === "sale") {
        return warehouse.free_qty || 0;
    }
    return warehouse.virtual_available || 0;
}

patch(QtyAtDateWidget.prototype, {
    initCalcData() {
        super.initCalcData();
        const {data} = this.props.record;
        this.calcData.multi_warehouse_partial = false;
        this.calcData.multi_warehouse_issue = false;
        if (!data.scheduled_date) {
            return;
        }
        const breakdown = data.qty_at_date_per_warehouse || [];
        const total = breakdown.reduce(
            (sum, warehouse) => sum + warehouseQty(data, warehouse),
            0
        );
        this.calcData.total_all_warehouses = total;
        this.calcData.fulfilled_all_warehouses = total >= data.qty_to_deliver;
        this.calcData.multi_warehouse_partial =
            !this.calcData.will_be_fulfilled && this.calcData.fulfilled_all_warehouses;
        this.calcData.multi_warehouse_issue =
            !this.calcData.will_be_fulfilled && !this.calcData.fulfilled_all_warehouses;
    },

    updateCalcData() {
        super.updateCalcData();
        const {data} = this.props.record;
        if (!data.scheduled_date) {
            return;
        }
        const breakdown = data.qty_at_date_per_warehouse || [];
        const ownWarehouseId = data.warehouse_id && data.warehouse_id[0];
        this.calcData.uom_name = data.product_uom && data.product_uom[1];
        this.calcData.warehouse_breakdown = breakdown.map((warehouse) => ({
            id: warehouse.warehouse_id,
            name: warehouse.warehouse_name,
            qty: warehouseQty(data, warehouse),
            is_current: warehouse.warehouse_id === ownWarehouseId,
        }));
    },
});
