import {patch} from "@web/core/utils/patch";
import {WebsiteSale} from "@website_sale/interactions/website_sale";
import wSaleUtils from "@website_sale/js/website_sale_utils";

patch(WebsiteSale.prototype, {
    /**
     * Prevent "Enter" keypress in the quantity input
     * from submitting the form and reloading the page.
     * Keep rounding logic with manual input.
     *
     * @override
     */
    start() {
        const res = super.start?.(...arguments);

        this._onQtyKeydown = (ev) => {
            const input = ev.target;
            if (!input?.matches?.('input[name="add_qty"]')) return;
            if (ev.key !== "Enter") return;

            ev.preventDefault();
            ev.stopPropagation();

            // Force "change" including the multiple rounding
            input.dispatchEvent(new Event("change", {bubbles: true}));
        };

        this.el.addEventListener("keydown", this._onQtyKeydown, true);
        return res;
    },

    /**
     * Make sure to remove the event listener
     * when the widget is destroyed to prevent memory leaks.
     *
     * @override
     */
    destroy() {
        this.el?.removeEventListener?.("keydown", this._onQtyKeydown, true);
        this._onQtyKeydown = null;
        return super.destroy?.(...arguments);
    },

    /**
     * Resolve the root DOM node and return the add_qty input.
     */
    _getAddQtyInput(parent) {
        const root = parent?.el || parent?.[0] || parent || this.el;
        return root?.querySelector?.('input[name="add_qty"]');
    },

    /**
     * Read multiple step info from dataset.
     * Dataset is refreshed on each combination change.
     */
    _getMultipleInfoFromInput(input) {
        const isMultiple = input?.dataset?.isMultiple === "1";
        const step = parseFloat(input?.dataset?.saleMultipleQty || 1) || 1;
        return {isMultiple, step};
    },

    /**
     * Compute constraints for add_qty for both multiple/non-multiple cases.
     * For multiple products, effectiveMin must be >= step (we want one pack minimum).
     */
    _getAddQtyConstraints(input) {
        const min = parseFloat(input.dataset.min || 0);
        const max = parseFloat(input.dataset.max || Infinity);
        const {isMultiple, step} = this._getMultipleInfoFromInput(input);

        const effectiveMin = isMultiple ? Math.max(min, step) : min;
        return {min, max, isMultiple, step, effectiveMin};
    },

    /**
     * Update the dataset attributes for the quantity input
     * based on the selected combination with sale multiple info.
     *
     */
    updateSaleMultiple(parent, combination) {
        const input = this._getAddQtyInput(parent);
        if (!input) return;

        input.dataset.saleMultipleQty = String(combination?.sale_multiple_qty ?? 1);
        input.dataset.isMultiple = combination?.is_multiple ? "1" : "0";
    },

    /**
     * When the combination changes, update the dataset with sale multiple info.
     * Reset the quantity to the default value for the new variant
     * only if the variant has changed.
     *
     * @override
     */
    _onChangeCombination(ev, parent, combination) {
        const res = super._onChangeCombination?.(...arguments);

        this.updateSaleMultiple(parent, combination);

        // Reset to default only when switching variant.
        // This avoids "random" qty resets when only price/availability changes.
        if (combination?.variant_switched) {
            const input = this._getAddQtyInput(parent);
            if (!input) return res;

            const {isMultiple, step, effectiveMin} = this._getAddQtyConstraints(input);

            /**
             * Default qty per variant:
             * - multiple => at least one step (and still respect min if it is bigger)
             * - non-multiple => min
             */
            const defaultQty = isMultiple ? Math.max(step, effectiveMin) : effectiveMin;
            input.value = defaultQty;
        }

        return res;
    },

    /**
     * When the quantity is manually changed, apply rounding logic for multiples.
     *
     * @override
     */
    onChangeAddQuantity(ev) {
        const input = ev.currentTarget;

        // Non-multiple: keep standard logic.
        if (input.dataset.isMultiple !== "1") {
            return super.onChangeAddQuantity?.(...arguments);
        }

        const parent = wSaleUtils.getClosestProductForm(input);
        if (!parent) return;

        const {max, step, effectiveMin} = this._getAddQtyConstraints(input);

        let qty = parseFloat(input.value || 0);
        if (!Number.isFinite(qty) || qty <= 0) {
            qty = effectiveMin;
        }

        // Always round UP to the step.
        qty = Math.ceil(qty / step - 1e-9) * step;

        // Clamp to constraints (multiple effective min + max)
        qty = Math.min(Math.max(qty, effectiveMin), max);
        if (qty !== parseFloat(input.value || 0)) {
            input.value = qty;
        }

        // Keep standard behavior
        this.triggerVariantChange(parent);
    },

    /**
     * Apply a new qty to the input and trigger change.
     * This keeps one place where we dispatch the event.
     */
    _applyAddQtyAndTriggerChange(input, newQty) {
        const previousQty = parseFloat(input.value || 0);
        if (newQty === previousQty) return;

        input.value = newQty;
        input.dispatchEvent(new Event("change", {bubbles: true}));
    },

    /**
     * When the "+" or "-" buttons are clicked, update the quantity
     * according to the step and respecting the min/max constraints for multiples.
     *
     * @override
     */
    onChangeQuantity(ev) {
        const btn = ev?.currentTarget;
        const group = btn?.closest?.(".input-group");
        const input = group?.querySelector?.('input[name="add_qty"]');
        if (!input) return;

        // Non-multiple: keep standard behavior.
        if (input.dataset.isMultiple !== "1") {
            return super.onChangeQuantity?.(...arguments);
        }

        const {max, step, effectiveMin} = this._getAddQtyConstraints(input);

        const previousQty = parseFloat(input.value || 0);
        const delta = btn.name === "remove_one" ? -step : step;
        const quantity = previousQty + delta;

        /**
         * For multiple products:
         * - enforce effectiveMin (>= step)
         * - clamp to max
         * - we do not go below effectiveMin (product page does not support "0" remove)
         */
        const newQty = Math.min(Math.max(quantity, effectiveMin), max);

        this._applyAddQtyAndTriggerChange(input, newQty);
    },
});
