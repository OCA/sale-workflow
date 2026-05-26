/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogSearchPanel} from "@product/product_catalog/search/search_panel";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(ProductCatalogSearchPanel.prototype, {
    updateActiveValues() {
        super.updateActiveValues(...arguments);
        for (const section of this.sections) {
            if (
                section.fieldName === "catalog_price_mode" &&
                section.values.has(false)
            ) {
                section.values.get(false).display_name = _t("Pricelist");
            }
        }
    },
});
