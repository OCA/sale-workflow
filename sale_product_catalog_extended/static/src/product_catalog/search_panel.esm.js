/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogSearchPanel} from "@product/product_catalog/search/search_panel";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(ProductCatalogSearchPanel.prototype, {
    get sections() {
        const context = this.env.searchModel.globalContext;
        const isActive = (fieldName, value) =>
            this.env.searchModel.categories.some(
                (category) =>
                    category.fieldName === fieldName && category.activeValueId === value
            );
        const hidden = [];
        // The history partner is only shown when enabled in the settings (its
        // default applies anyway), and it only matters for the last sales and the
        // last sale price, so hide it while neither of them is active.
        if (
            !context.catalog_show_history_partner ||
            !(
                isActive("catalog_last_sales", "last_sales") ||
                isActive("catalog_price_mode", "last_price")
            )
        ) {
            hidden.push("catalog_history_partner");
        }
        // The sort is only shown when enabled in the settings (its default
        // applies anyway).
        if (!context.catalog_show_sort) {
            hidden.push("catalog_sort");
        }
        return super.sections.filter((section) => !hidden.includes(section.fieldName));
    },
    updateActiveValues() {
        super.updateActiveValues(...arguments);
        for (const section of this.sections) {
            if (
                section.fieldName === "catalog_origin_data" &&
                section.values.has(false)
            ) {
                section.values.get(false).display_name = _t("Products");
            }
            if (
                section.fieldName === "catalog_price_mode" &&
                section.values.has(false)
            ) {
                section.values.get(false).display_name = _t("Pricelist");
            }
            if (
                section.fieldName === "catalog_history_partner" &&
                section.values.has(false)
            ) {
                section.values.get(false).display_name = _t("Customer");
            }
            if (section.fieldName === "catalog_sort" && section.values.has(false)) {
                section.values.get(false).display_name = _t("Default");
            }
        }
    },
});
