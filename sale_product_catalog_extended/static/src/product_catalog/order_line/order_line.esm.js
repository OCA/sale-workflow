/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogOrderLine} from "@product/product_catalog/order_line/order_line";
import {patch} from "@web/core/utils/patch";
import {formatMonetary} from "@web/views/fields/formatters";

patch(ProductCatalogOrderLine.prototype, {
    displayEdit() {
        return this.env.orderResModel === "sale.order";
    },
    get price() {
        if (
            this.props.catalogShowLastPrice &&
            this.props.lastPrice &&
            !this.isInOrder()
        ) {
            const {currencyId, digits} = this.env;
            return formatMonetary(this.props.lastPrice, {currencyId, digits});
        }
        return super.price;
    },
});

ProductCatalogOrderLine.props = {
    ...ProductCatalogOrderLine.props,
    lastPrice: {type: Number, optional: true},
    catalogShowLastPrice: {type: Boolean, optional: true},
    lineId: {type: Number, optional: true},
};
