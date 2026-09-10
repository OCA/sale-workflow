/* Copyright 2025 Tecnativa - Carlos Roca
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
            const lines = item.record?.productCatalogData?.lines;
            if (lines?.length > 1) {
                for (const line of lines) {
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
                        key: `${item.key}_line_${line.lineId}`,
                    });
                }
            } else {
                result.push(item);
            }
        }
        return result;
    },
});
