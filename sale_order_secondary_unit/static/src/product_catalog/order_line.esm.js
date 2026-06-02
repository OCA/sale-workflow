/** @odoo-module */

import {ProductCatalogOrderLine} from "@product/product_catalog/order_line/order_line";

// Allow the name of the unit added to the order to flow through the catalog
// data so it can be displayed next to the quantity input.
ProductCatalogOrderLine.props = {
    ...ProductCatalogOrderLine.props,
    uomToAdd: {type: String, optional: true},
};
