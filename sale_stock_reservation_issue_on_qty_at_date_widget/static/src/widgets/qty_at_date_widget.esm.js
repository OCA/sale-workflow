/** @odoo-module **/

import {QtyAtDateWidget} from "@sale_stock/widgets/qty_at_date_widget";

import {patch} from "@web/core/utils/patch";

patch(
    QtyAtDateWidget.prototype,
    "sale_stock_reservation_issue_on_qty_at_date_widget.QtyAtDateWidget",
    {
        initCalcData() {
            this._super();
            const {data} = this.props.record;
            if (["draft", "sent"].includes(data.state)) {
                this.calcData.reservation_issue =
                    data.free_qty_today < data.qty_to_deliver;
            }
        },
    }
);
