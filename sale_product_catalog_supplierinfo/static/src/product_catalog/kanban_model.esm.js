/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogKanbanModel} from "@product/product_catalog/kanban_model";
import {patch} from "@web/core/utils/patch";

patch(ProductCatalogKanbanModel.prototype, {
    _getOrderLinesInfoParams(params, productIds) {
        const baseParams = super._getOrderLinesInfoParams(params, productIds);
        // Supplier origin only applies to the sale catalog. Avoid leaking the
        // kwarg to other catalogs (e.g. purchase) whose backend methods do not
        // accept it.
        if (baseParams.res_model !== "sale.order") {
            return baseParams;
        }
        // Tell the backend that the supplier origin is selected so it splits the
        // product cards into one card per vendor.
        const catalogOriginSupplierinfo = (params.domain || []).some(
            (cond) =>
                Array.isArray(cond) &&
                cond[0] === "catalog_origin_data" &&
                cond[2] === "supplierinfo"
        );
        return {
            ...baseParams,
            catalog_origin_supplierinfo: catalogOriginSupplierinfo,
        };
    },
});
