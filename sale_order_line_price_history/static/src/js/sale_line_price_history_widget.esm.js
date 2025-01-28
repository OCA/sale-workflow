import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";
import {useService} from "@web/core/utils/hooks";

export class PriceHistoryWidget extends Component {
    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    viewPriceHistory() {
        this.actionService.doAction(
            "sale_order_line_price_history.sale_order_line_price_history_action",
            {
                additionalContext: {
                    default_product_id: this.props.record.data.product_id[0],
                    default_partner_id: this.props.record.data.order_partner_id[0],
                    default_active_id: this.props.value,
                    default_sale_order_line_id: this.props.value,
                },
                onClose: (value) => {
                    if (value && "price_unit" in value) {
                        this.props.record.update(value);
                    }
                },
            }
        );
    }
}

PriceHistoryWidget.template = "sale_order_line_price_history.price_history_widget";
PriceHistoryWidget.props = {
    ...standardWidgetProps,
    // Onchange decorator returns an undefined value for the id instead of false
    value: {optional: true},
};

registry
    .category("view_widgets")
    .add("sale_line_price_history_widget", {component: PriceHistoryWidget});
