/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogKanbanModel} from "@product/product_catalog/kanban_model";
import {patch} from "@web/core/utils/patch";

patch(ProductCatalogKanbanModel.prototype, {
    _getOrderLinesInfoParams(params, productIds) {
        const baseParams = super._getOrderLinesInfoParams(params, productIds);
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
