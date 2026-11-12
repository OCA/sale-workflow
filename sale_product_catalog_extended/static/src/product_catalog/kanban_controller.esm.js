/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogKanbanController} from "@product/product_catalog/kanban_controller";
import {patch} from "@web/core/utils/patch";

patch(ProductCatalogKanbanController.prototype, {
    get isSaleOrder() {
        return this.orderResModel === "sale.order";
    },

    get displayConfirm() {
        return (
            this.isSaleOrder && ["draft", "sent"].includes(this.orderStateInfo?.state)
        );
    },

    get className() {
        const className = super.className;
        // The rows layout does not fit the narrow columns of a grouped view.
        if (this.props.context.catalog_layout !== "rows" || this.model.root.isGrouped) {
            return className;
        }
        return [className, "o_product_catalog_rows"].filter(Boolean).join(" ");
    },

    async onClickConfirm() {
        await this.orm.call("sale.order", "action_confirm", [[this.orderId]], {
            context: {validate_analytic: true},
        });
        await this.backToQuotation();
    },
});
