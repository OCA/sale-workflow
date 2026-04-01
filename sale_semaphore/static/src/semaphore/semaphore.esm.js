// Copyright 2026 Tecnativa - Carlos Roca
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import {
    SelectionField,
    selectionField,
} from "@web/views/fields/selection/selection_field";
import {Component} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {usePopover} from "@web/core/popover/popover_hook";
import {useService} from "@web/core/utils/hooks";

export class SemaphorePopover extends Component {
    static template = "sale_semaphore.SemaphorePopover";
    static props = {
        record: Object,
        close: Function,
    };
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.notification = useService("notification");
    }
    onClickSetPriceSuccess() {
        this.props.record.update({
            price_unit: this.props.record.data.semaphore_max_price_success,
            discount: 0,
        });
        this.props.close();
    }
    onClickSetPriceWarning() {
        this.props.record.update({
            price_unit: this.props.record.data.semaphore_max_price_warning,
            discount: 0,
        });
        this.props.close();
    }
    onClickSetPriceDanger() {
        this.props.record.update({
            price_unit: this.props.record.data.semaphore_max_price_danger,
            discount: 0,
        });
        this.props.close();
    }
    async onClickResetPrice() {
        this.props.record.update({
            product_id: this.props.record.data.product_id,
        });
        this.props.close();
    }
}

export class Semaphore extends SelectionField {
    static components = {Popover: SemaphorePopover};
    static template = "sale_semaphore.SemaphoreField";

    setup() {
        super.setup(...arguments);
        this.popover = usePopover(this.constructor.components.Popover, {
            position: "left",
        });
        this.notification = useService("notification");
    }
    get string() {
        if (this.type === "selection") {
            return this.props.record.data[this.props.name]
                ? this.options.find(
                      (o) => o[0] === this.props.record.data[this.props.name]
                  )[1]
                : "";
        }
        return super.string;
    }
    _getSupportedModels() {
        return ["sale.order.line"];
    }
    onClickSemaphore(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        if (!this._getSupportedModels().includes(this.props.record.resModel)) {
            this.notification.add(
                _t("The semaphore assignation does not work in this model."),
                {
                    type: "info",
                }
            );
        } else if (this.props.record.data.semaphore_active) {
            this.initPopover(ev);
        } else {
            this.notification.add(
                _t("The product or its category has not the semaphore activated."),
                {
                    type: "info",
                }
            );
        }
    }
    initPopover(ev) {
        this.popover.open(ev.currentTarget, {
            record: this.props.record,
        });
    }
}

export const semaphoreField = {
    ...selectionField,
    component: Semaphore,
};

registry.category("fields").add("semaphore", semaphoreField);
