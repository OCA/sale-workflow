/** @odoo-module **/

import {registry} from "@web/core/registry";
import {usePopover} from "@web/core/popover/popover_hook";
import {useService} from "@web/core/utils/hooks";

const {Component, EventBus, onWillRender} = owl;

export class PriceComplianceTierPopover extends Component {
    setup() {
        this.actionService = useService("action");
    }
}

PriceComplianceTierPopover.template =
    "sale_price_compliance.PriceComplianceTierPopover";
PriceComplianceTierPopover.position = "right";

export class PriceComplianceTierWidget extends Component {
    setup() {
        this.bus = new EventBus();
        this.popover = usePopover();
        this.closePopover = null;
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
        this.closePopover = this.popover.add(
            ev.currentTarget,
            this.constructor.components.Popover,
            {
                bus: this.bus,
                record: this.props.record,
                calcData: this.calcData,
            },
            {
                position: "top",
                // Ensure popup full width on kanban
                popoverClass: "mw-100",
            }
        );
        this.bus.addEventListener("close-popover", this.closePopover);
    }
}

PriceComplianceTierWidget.components = {Popover: PriceComplianceTierPopover};
PriceComplianceTierWidget.template = "sale_price_compliance.PriceComplianceTier";

registry
    .category("view_widgets")
    .add("price_compliance_tier_widget", PriceComplianceTierWidget);
