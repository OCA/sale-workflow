/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogKanbanModel} from "@product/product_catalog/kanban_model";
import {patch} from "@web/core/utils/patch";

patch(ProductCatalogKanbanModel.prototype, {
    _getOrderLinesInfoParams(params, productIds) {
        const baseParams = super._getOrderLinesInfoParams(params, productIds);
        // The last price feature is sale specific. Other catalogs (e.g. purchase)
        // would forward this kwarg down to methods that do not accept it
        // (PurchaseOrder._get_product_catalog_record_lines).
        if (baseParams.res_model !== "sale.order") {
            return baseParams;
        }
        const catalogShowLastPrice = (params.domain || []).some(
            (cond) =>
                Array.isArray(cond) &&
                cond[0] === "catalog_price_mode" &&
                cond[2] === "last_price"
        );
        return {
            ...baseParams,
            catalog_show_last_price: catalogShowLastPrice,
        };
    },
});
