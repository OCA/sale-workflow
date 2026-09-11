/** @odoo-module **/

import {registry} from "@web/core/registry";
import {usePopover} from "@web/core/popover/popover_hook";
import {Component} from "@odoo/owl";
import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";

export class QtyPerWarehousePopover extends Component {
    static template =
        "sale_order_line_display_stock_per_warehouse.QtyPerWarehousePopover";
    static props = {
        record: Object,
        close: Function,
    };
}

export class QtyPerWarehouseWidget extends Component {
    static components = {Popover: QtyPerWarehousePopover};
    static template = "sale_order_line_display_stock_per_warehouse.QtyPerWarehouse";
    static props = {...standardWidgetProps};
    setup() {
        this.popover = usePopover(this.constructor.components.Popover, {
            position: "top",
        });
    }
    async showPopup(ev) {
        const target = ev.currentTarget;
        this.popover.open(target, {
            record: this.props.record,
        });
    }
}

export const qtyPerWarehouseWidget = {
    component: QtyPerWarehouseWidget,
    fieldDependencies: [
        {name: "display_qty_per_warehouse_widget", type: "boolean"},
        {name: "qty_per_warehouse_widget_data", type: "binary"},
    ],
};
registry
    .category("view_widgets")
    .add("qty_per_warehouse_widget", qtyPerWarehouseWidget);
