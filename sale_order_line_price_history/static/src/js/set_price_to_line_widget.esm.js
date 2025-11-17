import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useService} from "@web/core/utils/hooks";

export class SetPriceToLineWidget extends Component {
    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    setPriceHistory() {
        const infos = {
            price_unit: this.props.record.data.price_unit,
        };
        if (this.props.record.data.discount !== undefined) {
            // Need to check if discount is availabe to avoid errors
            // if trying to define the value undefined
            infos.discount = this.props.record.data.discount;
        }
        this.actionService.doAction({
            type: "ir.actions.act_window_close",
            infos,
        });
    }
}

SetPriceToLineWidget.template =
    "sale_order_line_price_history.price_to_line_history_widget";
SetPriceToLineWidget.props = standardFieldProps;

// Add the field to the correct category
registry
    .category("fields")
    .add("set_price_to_line_widget", {component: SetPriceToLineWidget});
