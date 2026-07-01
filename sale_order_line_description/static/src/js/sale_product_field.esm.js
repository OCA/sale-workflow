/* Copyright 2026 Moduon
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {SaleOrderLineProductField} from "@sale/js/sale_product_field";
import {onWillStart} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {user} from "@web/core/user";

patch(SaleOrderLineProductField.prototype, {
    setup() {
        super.setup(...arguments);
        this.useProductDescriptionPerSOLine = false;
        onWillStart(async () => {
            this.useProductDescriptionPerSOLine = await user.hasGroup(
                "sale_order_line_description.group_use_product_description_per_so_line"
            );
        });
    },

    parseLabel(value) {
        if (this.useProductDescriptionPerSOLine) {
            return value || "";
        }
        return super.parseLabel(value);
    },
});
