/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogKanbanRecord} from "@product/product_catalog/kanban_record";
import {patch} from "@web/core/utils/patch";
import {rpc} from "@web/core/network/rpc";
import {useService} from "@web/core/utils/hooks";
import {useSubEnv} from "@odoo/owl";

patch(ProductCatalogKanbanRecord.prototype, {
    setup() {
        super.setup();
        this.action = useService("action");
        useSubEnv({
            openOrderLine: this.onClickEditOrderLine.bind(this),
        });
    },
    async onClickEditOrderLine() {
        const order_line_ids = await rpc("/product/catalog/sale/open_order_line", {
            order_id: this.env.orderId,
            product_id: this.env.productId,
        });
        if (!this.productCatalogData.multiLine) {
            const action = await this.action.loadAction(
                "sale_product_catalog_extended.action_open_editable_sale_order_line"
            );
            return this.action.doAction(
                {
                    ...action,
                    res_id: order_line_ids[0],
                },
                {
                    onClose: () => {
                        this.updateRecordData(order_line_ids);
                    },
                }
            );
        }
        const action = await this.action.loadAction(
            "sale_product_catalog_extended.action_open_editable_sale_order_line_multi"
        );
        return this.action.doAction(
            {
                ...action,
                domain: [["id", "in", order_line_ids]],
            },
            {
                onClose: () => {
                    this.updateRecordData(order_line_ids);
                },
            }
        );
    },
    updateQuantity() {
        if (!this.productCatalogData.readOnly && this.productCatalogData.multiLine) {
            return;
        }
        super.updateQuantity(...arguments);
    },
    async updateRecordData(order_line_ids) {
        this.props.record.productCatalogData = await rpc(
            "/product/catalog/sale/get_order_line_data",
            {
                order_line_ids,
            }
        );
    },
});
