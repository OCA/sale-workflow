/** @odoo-module **/

import {
    QtyAtDatePopover,
    QtyAtDateWidget,
} from "@sale_stock/widgets/qty_at_date_widget";

import {formatDateTime} from "@web/core/l10n/dates";
import {localization} from "@web/core/l10n/localization";
import {patch} from "@web/core/utils/patch";

patch(
    QtyAtDatePopover.prototype,
    "sale_stock_expiry_date_on_qty_at_date_widget.QtyAtDatePopover",
    {
        async openViewExpiryDates() {
            const action = await this.actionService.loadAction(
                "sale_stock_expiry_date_on_qty_at_date_widget.action_open_quants_expiry_dates",
                this.props.context
            );
            action.domain = [
                ["product_id", "=", this.props.record.data.product_id[0]],
                ["location_id.usage", "=", "internal"],
            ];
            this.actionService.doAction(action, {
                additionalContext: {
                    single_product: true,
                    hide_location: true,
                    hide_lot: false,
                },
            });
        },
    }
);

patch(
    QtyAtDateWidget.prototype,
    "sale_stock_expiry_date_on_qty_at_date_widget.QtyAtDateWidget",
    {
        updateCalcData() {
            if (this.props.record.data.predicted_first_expiration_date) {
                this.calcData.predicted_first_expiration_date = formatDateTime(
                    this.props.record.data.predicted_first_expiration_date,
                    {format: localization.dateFormat}
                );
            }
            return this._super();
        },
    }
);
