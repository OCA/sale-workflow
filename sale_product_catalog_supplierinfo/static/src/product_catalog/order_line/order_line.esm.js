/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogOrderLine} from "@product/product_catalog/order_line/order_line";

ProductCatalogOrderLine.props = {
    ...ProductCatalogOrderLine.props,
    vendorId: {type: Number, optional: true},
    vendorName: {type: String, optional: true},
    vendorComment: {type: String, optional: true},
    supplierinfoId: {type: [Number, Boolean], optional: true},
};
