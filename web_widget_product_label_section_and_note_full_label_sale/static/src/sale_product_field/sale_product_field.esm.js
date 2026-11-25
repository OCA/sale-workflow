/* Copyright 2025 ForgeFlow S.L.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {SaleOrderLineProductField} from "@sale/js/sale_product_field";
import {patch} from "@web/core/utils/patch";

patch(SaleOrderLineProductField.prototype, {
    get label() {
        return this.props.record.data.name;
    },
    updateLabel(value) {
        if (!this.translatedProductName) {
            return super.updateLabel(value);
        }
        this.props.record.update({name: value || this.translatedProductName});
    },
});
