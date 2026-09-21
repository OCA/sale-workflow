/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {QtyAtDatePopover} from "@sale_stock/widgets/qty_at_date_widget";
import {useService} from "@web/core/utils/hooks";
import {onWillStart, useState} from "@odoo/owl";

patch(QtyAtDatePopover.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.state = useState({
            ...this.state,
            lotsLoading: true,
            lots: [],
            selectedLots: {},
            applying: false,
        });

        onWillStart(async () => {
            if (
                this.props.record.data.product_type === "consu" &&
                this.props.record.data.product_id
            ) {
                await this.fetchLots();
            }
        });
    },

    async fetchLots() {
        this.state.lotsLoading = true;
        try {
            const result = await this.orm.call(
                "sale.order.line",
                "get_available_lots_for_line",
                [[this.props.record.resId]]
            );
            this.state.lots = result.available || [];

            // Prefill with aggregated lots from the backend
            if (result.selected) {
                Object.assign(this.state.selectedLots, result.selected);
            }

            // Also prefill current line if it was just selected and not yet saved
            if (this.props.record.data.lot_id) {
                const lotData = this.props.record.data.lot_id;
                const existingLotId = Array.isArray(lotData)
                    ? lotData[0]
                    : lotData.id || lotData;
                // Only overwrite if it wasn't already loaded from backend
                if (!this.state.selectedLots[existingLotId]) {
                    this.state.selectedLots[existingLotId] =
                        this.props.record.data.product_uom_qty || 0;
                }
            }
        } catch (error) {
            console.error("Error fetching lots", error);
        } finally {
            this.state.lotsLoading = false;
        }
    },

    onLotQtyChange(ev) {
        const lotId = parseInt(ev.target.dataset.lotId, 10);
        let qty = parseFloat(ev.target.value) || 0;
        const maxQty = parseFloat(ev.target.max) || 0;

        if (qty > maxQty) {
            qty = maxQty;
            ev.target.value = maxQty;
        }

        if (qty > 0) {
            this.state.selectedLots[lotId] = qty;
        } else {
            delete this.state.selectedLots[lotId];
        }
    },

    async applyLotsSelection() {
        this.state.applying = true;
        try {
            if (Object.keys(this.state.selectedLots).length > 0) {
                await this.orm.call("sale.order.line", "action_split_lines_by_lot", [
                    [this.props.record.resId],
                    this.state.selectedLots,
                ]);
                // Reload the view to show the new lines
                await this.props.record.model.root.load();
                this.props.close();
            }
        } catch (e) {
            console.error("Failed to split lines", e);
        } finally {
            this.state.applying = false;
        }
    },
});
