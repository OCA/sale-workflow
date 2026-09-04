/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogOrderLine} from "@product/product_catalog/order_line/order_line";
import {patch} from "@web/core/utils/patch";

patch(ProductCatalogOrderLine.prototype, {
    get showPrice() {
        // Vendor cards render the price inline (next to the vendor name) instead
        // of portalling it, because several vendor cards share the same product
        // and would otherwise collide on the same #product-<id>-price target.
        if (this.props.vendorId) {
            return false;
        }
        return super.showPrice;
    },
});

ProductCatalogOrderLine.props = {
    ...ProductCatalogOrderLine.props,
    vendorId: {type: Number, optional: true},
    vendorName: {type: String, optional: true},
    vendorComment: {type: String, optional: true},
    supplierinfoId: {type: [Number, Boolean], optional: true},
};
