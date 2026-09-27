/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogSearchPanel} from "@product/product_catalog/search/search_panel";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(ProductCatalogSearchPanel.prototype, {
    get sections() {
        // The history partner is only shown when enabled in the settings (its
        // default applies anyway), and it only matters for the last sales and the
        // last sale price, so hide it while neither of them is active.
        const shown = Boolean(
            this.env.searchModel.globalContext.catalog_show_history_partner
        );
        const isActive = (fieldName, value) =>
            this.env.searchModel.categories.some(
                (category) =>
                    category.fieldName === fieldName && category.activeValueId === value
            );
        if (
            shown &&
            (isActive("catalog_last_sales", "last_sales") ||
                isActive("catalog_price_mode", "last_price"))
        ) {
            return super.sections;
        }
        return super.sections.filter(
            (section) => section.fieldName !== "catalog_history_partner"
        );
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
        }
    },
});
