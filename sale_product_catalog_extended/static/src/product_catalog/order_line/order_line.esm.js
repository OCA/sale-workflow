/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {onMounted, t, useProps} from "@odoo/owl";
import {ProductCatalogOrderLine} from "@product/product_catalog/order_line/order_line";
import {formatMonetary} from "@web/views/fields/formatters";
import {patch} from "@web/core/utils/patch";

patch(ProductCatalogOrderLine.prototype, {
    setup() {
        super.setup();
        this.catalogExtendedProps = useProps({
            lastPrice: t.number().optional(),
            catalogShowLastPrice: t.boolean().optional(),
            catalogUseDeliveryAddress: t.boolean().optional(),
            lineId: t.number().optional(),
        });
        // Show the price in the own card, as several cards can show the same
        // product (one per order line or vendor), sharing the product-level
        // #product-{id}-price element.
        onMounted(() => {
            const cardKey = this.env.catalogCardKey;
            const target =
                cardKey &&
                document.querySelector(
                    `[data-catalog-card="${cardKey}"] [name="o_kanban_price"]`
                );
            if (target) {
                this.portalTarget.set(target);
            }
        });
    },
    displayEdit() {
        return this.env.orderResModel === "sale.order";
    },
    get price() {
        const {catalogShowLastPrice, lastPrice} = this.catalogExtendedProps;
        if (catalogShowLastPrice && lastPrice && !this.isInOrder()) {
            const {currencyId, digits} = this.env;
            return formatMonetary(lastPrice, {currencyId, digits});
        }
        return super.price;
    },
});
