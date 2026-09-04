/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogKanbanController} from "@product/product_catalog/kanban_controller";
import {patch} from "@web/core/utils/patch";
import {useState} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";

patch(ProductCatalogKanbanController.prototype, {
    setup() {
        super.setup();
        this.saleOrderState = useState({state: false});
    },

    get isSaleOrder() {
        return this.orderResModel === "sale.order";
    },

    async _defineButtonContent() {
        if (!this.isSaleOrder) {
            return super._defineButtonContent();
        }
        const [orderData] = await this.orm.searchRead(
            "sale.order",
            [["id", "=", this.orderId]],
            ["state"]
        );
        const orderIsQuotation = ["draft", "sent"].includes(orderData.state);
        this.buttonString = orderIsQuotation
            ? _t("Back to Quotation")
            : _t("Back to Order");
        this.saleOrderState.state = orderData.state;
    },

    async onClickConfirm() {
        await this.orm.call("sale.order", "action_confirm", [[this.orderId]], {
            context: {validate_analytic: true},
        });
        await this.backToQuotation();
    },
});
