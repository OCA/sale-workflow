import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";
import {usePopover} from "@web/core/popover/popover_hook";

export class QtyByWarehousePopover extends Component {
    static template = "sale_stock_qty_by_warehouse.QtyByWarehousePopover";
    static props = {
        record: Object,
        close: Function,
    };
}

export class QtyByWarehouseWidget extends Component {
    static components = {Popover: QtyByWarehousePopover};
    static template = "sale_stock_qty_by_warehouse.QtyByWarehouse";
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

export const qtyByWarehouseWidget = {
    component: QtyByWarehouseWidget,
    fieldDependencies: [
        {name: "display_qty_by_warehouse_widget", type: "boolean"},
        {name: "qty_by_warehouse_widget_data", type: "binary"},
    ],
};
registry.category("view_widgets").add("qty_by_warehouse_widget", qtyByWarehouseWidget);
