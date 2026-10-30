import {Component, useProps} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";
import {useService} from "@web/core/utils/hooks";

export class PriceHistoryWidget extends Component {
    static template = "sale_order_line_price_history.price_history_widget";
    props = useProps(standardWidgetProps);

    setup() {
        this.actionService = useService("action");
    }

    viewPriceHistory() {
        const lineId = this.props.record.resId || false;
        this.actionService.doAction(
            "sale_order_line_price_history.sale_order_line_price_history_action",
            {
                additionalContext: {
                    default_product_id: this.props.record.data.product_id.id,
                    default_partner_id: this.props.record.data.order_partner_id.id,
                    active_id: lineId,
                    default_sale_order_line_id: lineId,
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

registry
    .category("view_widgets")
    .add("sale_line_price_history_widget", {component: PriceHistoryWidget});
