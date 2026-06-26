/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogKanbanRenderer} from "@product/product_catalog/kanban_renderer";
import {patch} from "@web/core/utils/patch";

patch(ProductCatalogKanbanRenderer.prototype, {
    getGroupsOrRecords() {
        const items = super.getGroupsOrRecords();
        if (this.props.list.isGrouped) {
            return items;
        }
        const result = [];
        for (const item of items) {
            const vendorLines = item.record?.productCatalogData?.vendorLines;
            // For the supplier origin, render one card per vendor reusing the
            // record but swapping its productCatalogData by the vendor line data.
            if (vendorLines?.length) {
                for (const line of vendorLines) {
                    const lineRecord = Object.create(item.record);
                    Object.defineProperty(lineRecord, "productCatalogData", {
                        get() {
                            return line;
                        },
                        configurable: true,
                    });
                    result.push({
                        ...item,
                        record: lineRecord,
                        // Include the line id so several lines of the same
                        // vendor get distinct (non colliding) card keys.
                        key: `${item.key}_vendor_${line.vendorId || 0}_${
                            line.lineId || "new"
                        }`,
                    });
                }
            } else {
                result.push(item);
            }
        }
        return result;
    },
});
