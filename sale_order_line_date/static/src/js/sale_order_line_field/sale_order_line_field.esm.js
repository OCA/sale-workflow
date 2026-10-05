/* Copyright 2025 SpritIT Ltd - Tatiana Deribina */

import {SaleOrderLineListRenderer} from "@sale/js/sale_order_line_field/sale_order_line_field";
import {patch} from "@web/core/utils/patch";

patch(SaleOrderLineListRenderer.prototype, {
    get comboColumns() {
        const columns = super.comboColumns;
        columns.push("commitment_date");
        return columns;
    },
});
