import {CartLine} from "@website_sale/interactions/cart_line";
import {patch} from "@web/core/utils/patch";

patch(CartLine.prototype, {
    /**
     * Prevent "Enter" keypress in the cart quantity input
     * from being ignored by the browser and leaving a stale value.
     * Keep rounding logic with manual input.
     *
     * @override
     */
    setup() {
        super.setup?.(...arguments);

        // Keydown capture handler to intercept Enter before default handlers.
        this._onQtyKeydown = (ev) => {
            const input = ev.target;

            // Only handle the cart qty input inside `.css_quantity`
            if (!input?.matches?.(".css_quantity > input.js_quantity")) return;
            if (ev.key !== "Enter") return;
            ev.preventDefault();
            ev.stopPropagation();

            // Force the standard "change" flow (including the rounding).
            input.dispatchEvent(new Event("change", {bubbles: true}));
        };

        this.el.addEventListener("keydown", this._onQtyKeydown, true);
    },

    /**
     * Make sure to remove the event listener
     * when the interaction is destroyed to prevent memory leaks.
     *
     * @override
     */
    destroy() {
        this.el?.removeEventListener?.("keydown", this._onQtyKeydown, true);
        this._onQtyKeydown = null;
        return super.destroy?.(...arguments);
    },

    /**
     * Read "sale multiple" info from the cart quantity input dataset.
     *
     */
    _getMultipleStep(input) {
        const isMultiple = input?.dataset?.isMultiple === "1";
        const step = isMultiple
            ? parseFloat(input.dataset.saleMultipleQty || 1) || 1
            : 1;
        return {isMultiple, step};
    },

    /**
     * Round the quantity UP to the nearest step.
     * Preserve 0 to keep the standard cart removal behavior.
     */
    _roundUpToStep(qty, step) {
        let value = parseFloat(qty || 0);
        if (!Number.isFinite(value)) value = 0;
        if (value <= 0) return 0;

        // -1e-9 prevents rounding artifacts when value is already a multiple.
        return Math.ceil(value / step - 1e-9) * step;
    },

    /**
     * Snap the input value to a valid quantity for multiple products
     * and apply the max constraint (if provided).
     *
     * Returns the new numeric quantity (or rawQty for non-multiple products).
     */
    _snapMultipleQuantity(input, rawQty) {
        const {isMultiple, step} = this._getMultipleStep(input);
        if (!isMultiple) return rawQty;

        let newQty = this._roundUpToStep(rawQty, step);

        // Respect cart max if present on the input
        const maxQty = parseFloat(input.dataset.max || Infinity);
        if (Number.isFinite(maxQty)) {
            newQty = Math.min(newQty, maxQty);
        }

        input.value = String(newQty);
        return newQty;
    },

    /**
     * When the quantity is manually changed, apply rounding logic for multiples.
     *
     * @override
     */
    async changeQuantity(ev, currentTargetEl) {
        const input = currentTargetEl;
        const {isMultiple} = this._getMultipleStep(input);

        // Non-multiple products: keep standard behavior.
        if (!isMultiple) {
            return await super.changeQuantity(ev, currentTargetEl);
        }

        // Multiple products: snap then apply the change through the standard pipeline.
        const rawQty = parseFloat(input.value || 0);
        this._snapMultipleQuantity(input, rawQty);

        return await this._changeQuantity(input);
    },

    /**
     * When the "+" or "-" buttons are clicked, update the quantity
     * according to the step and keep 0 as a valid "remove" value.
     *
     * IMPORTANT: for multiple products we must not call super,
     * because super applies +/- 1 and would break the step logic.
     *
     * @override
     */
    async incOrDecQuantity(ev, currentTargetEl) {
        const input = currentTargetEl
            .closest(".css_quantity")
            ?.querySelector("input.js_quantity");
        if (!input) {
            return await super.incOrDecQuantity(ev, currentTargetEl);
        }

        const {isMultiple, step} = this._getMultipleStep(input);
        if (!isMultiple) {
            return await super.incOrDecQuantity(ev, currentTargetEl);
        }

        const oldQty = parseFloat(input.value || 0) || 0;
        const isMinus = currentTargetEl
            .querySelector("i")
            ?.classList?.contains("oi-minus");

        /**
         * For multiples:
         * - plus => +step
         * - minus => -step
         * - if it goes below one step => 0 (remove line behavior)
         */
        let rawQty = 0;
        if (isMinus) {
            rawQty = oldQty - step;
            if (rawQty < step) rawQty = 0;
        } else {
            rawQty = oldQty + step;
        }

        this._snapMultipleQuantity(input, rawQty);

        return await this._changeQuantity(input);
    },
});
