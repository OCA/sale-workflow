/** @odoo-module **/

import {formatDateTime} from "@web/core/l10n/dates";
import {localization} from "@web/core/l10n/localization";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {usePopover} from "@web/core/popover/popover_hook";

const {Component, EventBus} = owl;

export class QtyAtDateByWarehousePopover extends Component {
    setup() {
        this.actionService = useService("action");
        this.formatData(this.props.record.data.qty_by_warehouse);
    }

    formatData(qty_by_warehouse) {
        const warehouses = JSON.parse(JSON.stringify(qty_by_warehouse));
        this.warehouses = warehouses;
    }

    openForecast(warehouse) {
        this.actionService.doAction(
            "stock.stock_replenishment_product_product_action",
            {
                additionalContext: {
                    active_model: "product.product",
                    active_id: this.props.record.data.product_id[0],
                    warehouse: warehouse.warehouse,
                    move_to_match_ids: this.props.record.data.move_ids.records.map(
                        (record) => record.data.id
                    ),
                    sale_line_to_match_id: this.props.record.data.id,
                },
            }
        );
    }
}

QtyAtDateByWarehousePopover.template =
    "sale_order_line_multi_warehouse.QtyDetailByWarehousePopOver";

export class QtyAtDateByWarehouseWidget extends Component {
    setup() {
        this.bus = new EventBus();
        this.popover = usePopover();
        this.closePopover = null;
        this.calcData = {};
        this.warehouses = JSON.parse(
            JSON.stringify(this.props.record.data.qty_by_warehouse)
        );
    }

    updateCalcData() {
        // Popup specific data
        const {data} = this.props.record;
        if (!data.scheduled_date) {
            return;
        }
        this.calcData.delivery_date = formatDateTime(data.scheduled_date, {
            format: localization.dateFormat,
        });
    }

    showPopup(ev) {
        this.updateCalcData();
        this.closePopover = this.popover.add(
            ev.currentTarget,
            this.constructor.components.Popover,
            {bus: this.bus, record: this.props.record, calcData: this.calcData},
            {
                position: "top",
            }
        );
        this.bus.addEventListener("close-popover", this.closePopover);
    }
}

QtyAtDateByWarehouseWidget.components = {Popover: QtyAtDateByWarehousePopover};
QtyAtDateByWarehouseWidget.template =
    "sale_order_line_multi_warehouse.qtyAtDateByWarehouse";

registry
    .category("view_widgets")
    .add("qty_at_date_by_warehouse_widget", QtyAtDateByWarehouseWidget);
