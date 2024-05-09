/** @odoo-module **/
const {Component} = owl;
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useService} from "@web/core/utils/hooks";

export class SetPriceToLineWidget extends Component {
    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    setPriceHistory() {
        this.actionService.doAction({
            type: "ir.actions.act_window_close",
            infos: {
                price_unit: this.props.record.data.price_unit,
                discount: this.props.record.data.discount,
            },
        });
    }
}

SetPriceToLineWidget.template =
    "sale_order_line_price_history.price_to_line_history_widget";
SetPriceToLineWidget.props = standardFieldProps;

// Add the field to the correct category
registry.category("fields").add("set_price_to_line_widget", SetPriceToLineWidget);
