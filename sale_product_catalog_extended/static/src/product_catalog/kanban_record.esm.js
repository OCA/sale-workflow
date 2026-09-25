/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogKanbanRecord} from "@product/product_catalog/kanban_record";
import {useSubEnv} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {rpc} from "@web/core/network/rpc";
import {useService} from "@web/core/utils/hooks";
import {ImageZoomDialog} from "./image_zoom_dialog.esm";

patch(ProductCatalogKanbanRecord.prototype, {
    setup() {
        super.setup();
        this.action = useService("action");
        this.dialog = useService("dialog");
        useSubEnv({
            openOrderLine: this.onClickEditOrderLine.bind(this),
            addNewOrderLine: this.onClickAddNewOrderLine.bind(this),
            lineId: this.props.record.productCatalogData.lineId,
        });
    },
    async onClickAddNewOrderLine() {
        const action = await this.action.loadAction(
            "sale_product_catalog_extended.action_open_editable_sale_order_line"
        );
        return this.action.doAction(
            {
                ...action,
                context: {
                    default_order_id: this.env.orderId,
                    default_product_id: this.env.productId,
                },
            },
            {
                onClose: () => this.props.list.model.load(),
            }
        );
    },
    /**
     * The last sales origin is sale specific, so the menu entry is hidden on
     * the other catalogs (e.g. purchase).
     */
    get displayExcludeFromLastSales() {
        return this.env.orderResModel === "sale.order";
    },
    async onClickExcludeFromLastSales() {
        await rpc("/product/catalog/sale/exclude_from_last_sales", {
            order_id: this.env.orderId,
            product_id: this.env.productId,
        });
        // Reload so the card disappears when the last sales origin is active.
        await this.props.list.model.load();
    },
    onGlobalClick(ev) {
        if (ev.target.closest(".o_field_image")) {
            const src = `/web/image/product.product/${this.env.productId}/image_1920`;
            this.dialog.add(ImageZoomDialog, {
                src,
                title: this.props.record.data.name,
            });
            return;
        }
        super.onGlobalClick(ev);
    },
    async onClickEditOrderLine() {
        const lineId = this.props.record.productCatalogData.lineId;
        if (lineId) {
            const action = await this.action.loadAction(
                "sale_product_catalog_extended.action_open_editable_sale_order_line"
            );
            return this.action.doAction(
                {...action, res_id: lineId},
                {onClose: () => this.props.list.model.load()}
            );
        }
        const order_line_ids = await rpc("/product/catalog/sale/open_order_line", {
            order_id: this.env.orderId,
            product_id: this.env.productId,
        });
        const action = await this.action.loadAction(
            "sale_product_catalog_extended.action_open_editable_sale_order_line"
        );
        return this.action.doAction(
            {...action, res_id: order_line_ids[0]},
            {onClose: () => this.props.list.model.load()}
        );
    },
    updateQuantity(quantity) {
        // Optimistically show the last sale price as soon as the product is
        // added, so the displayed unit price does not flash from the pricelist
        // price to the last sale price while the (debounced) RPC is in flight.
        const data = this.props.record.productCatalogData;
        if (quantity && data.catalogShowLastPrice && data.lastPrice) {
            data.price = data.lastPrice;
        }
        return super.updateQuantity(quantity);
    },
    async _updateQuantity() {
        const lineId = this.props.record.productCatalogData.lineId;
        if (lineId) {
            await rpc("/product/catalog/sale/update_line_qty", {
                line_id: lineId,
                quantity: this.productCatalogData.quantity,
            });
            await this.props.list.model.load();
            return;
        }
        return super._updateQuantity(...arguments);
    },
    _getUpdateQuantityAndGetPriceParams() {
        return {
            ...super._getUpdateQuantityAndGetPriceParams(),
            catalog_show_last_price: Boolean(
                this.props.record.productCatalogData.catalogShowLastPrice
            ),
        };
    },
});

// Use our own dropdown menu template so the catalog specific entries can call
// component methods, which the view arch is not allowed to do.
ProductCatalogKanbanRecord.menuTemplate =
    "sale_product_catalog_extended.KanbanRecordMenu";
