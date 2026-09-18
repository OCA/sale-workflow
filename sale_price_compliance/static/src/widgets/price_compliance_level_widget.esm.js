import {Component, onWillRender} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";
import {usePopover} from "@web/core/popover/popover_hook";
import {useService} from "@web/core/utils/hooks";

export class PriceComplianceTierPopover extends Component {
    static template = "sale_price_compliance.PriceComplianceTierPopover";
    static props = {
        record: Object,
        calcData: Object,
        close: Function,
    };
    setup() {
        this.actionService = useService("action");
    }
}

export class PriceComplianceTierWidget extends Component {
    static components = {Popover: PriceComplianceTierPopover};
    static template = "sale_price_compliance.PriceComplianceTier";
    static props = {...standardWidgetProps};
    setup() {
        this.popover = usePopover(this.constructor.components.Popover, {
            position: "right",
        });
        this.calcData = {};
        onWillRender(() => {
            this.updateCalcData();
        });
    }

    updateCalcData() {
        const {data} = this.props.record;
        // Value to display on the widget
        const foundElement = (data.price_compliance_data || []).find(
            (element) => element.tier === data.price_compliance_tier
        );
        this.calcData.price_compliance_tier_display = foundElement
            ? foundElement.display[0]
            : null;
        this.calcData.currency_symbol = foundElement
            ? foundElement.currency_symbol
            : null;
        this.calcData.product_base_uom = foundElement
            ? foundElement.product_base_uom
            : null;
        // Get Tier 1 compliance data
        const foundL1Element = (data.price_compliance_data || []).find(
            (element) => element.tier === "t1"
        );
        this.calcData.product_price_in_base_uom = foundL1Element
            ? foundL1Element.price[1]
            : null;
    }

    showPopup(ev) {
        this.updateCalcData();
        this.popover.open(ev.currentTarget, {
            record: this.props.record,
            calcData: this.calcData,
        });
    }
}

export const priceComplianceTierWidget = {
    component: PriceComplianceTierWidget,
};
registry
    .category("view_widgets")
    .add("price_compliance_tier_widget", priceComplianceTierWidget);
