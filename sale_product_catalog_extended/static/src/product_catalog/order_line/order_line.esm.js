/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogOrderLine} from "@product/product_catalog/order_line/order_line";
import {patch} from "@web/core/utils/patch";

patch(ProductCatalogOrderLine.prototype, {
    displayEdit() {
        return this.env.orderResModel === "sale.order";
    },
});

ProductCatalogOrderLine.props = {
    ...ProductCatalogOrderLine.props,
    multiLine: {type: Boolean, optional: true},
};
