/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
// Ensure the catalog kanban view is registered before we extend it below.
import "@product/product_catalog/kanban_view";
import {SearchModel} from "@web/search/search_model";
import {registry} from "@web/core/registry";

// Search panel category sections whose selection (origin/price mode) must
// force the rest of the category sections to be recomputed.
const CATALOG_PANEL_FIELDS = ["catalog_origin_data", "catalog_price_mode"];

export class ProductCatalogSearchModel extends SearchModel {
    /**
     * Signature of the current catalog origin/price selection, used to detect
     * when it changes between reloads.
     */
    _catalogPanelSelectionKey() {
        return this.categories
            .filter((category) => CATALOG_PANEL_FIELDS.includes(category.fieldName))
            .map((category) => `${category.fieldName}:${category.activeValueId}`)
            .join("|");
    }

    async _reloadSections() {
        const selectionKey = this._catalogPanelSelectionKey();
        if (selectionKey !== this._catalogPanelLastSelectionKey) {
            // The catalog origin/price are search panel selections, so they are
            // excluded from the search domain that drives the base reload. As a
            // result the category sections (e.g. product category) would not be
            // refetched and would keep showing categories that do not match the
            // products of the selected origin. Force the reload so the category
            // tree is recomputed on top of the origin products.
            this.searchPanelInfo.shouldReload = true;
        }
        this._catalogPanelLastSelectionKey = selectionKey;
        return super._reloadSections(...arguments);
    }
}

// Attach the custom search model to the catalog kanban view so that selecting
// an origin recomputes the product category panel.
const viewsRegistry = registry.category("views");
if (viewsRegistry.contains("product_kanban_catalog")) {
    viewsRegistry.get("product_kanban_catalog").SearchModel = ProductCatalogSearchModel;
}
