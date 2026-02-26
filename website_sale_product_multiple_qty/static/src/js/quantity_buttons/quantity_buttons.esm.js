import {QuantityButtons} from "@sale/js/quantity_buttons/quantity_buttons";
import {patch} from "@web/core/utils/patch";

/**
 * Extend QuantityButtons props with "sale multiple" info
 */
patch(QuantityButtons, {
    props: {
        ...QuantityButtons.props,
        isMultiple: {type: [Boolean, Number], optional: true},
        saleMultipleQty: {type: Number, optional: true},
    },
});

patch(QuantityButtons.prototype, {
    /**
     * Get the step and isMultiple values from component props.
     *
     */
    _getMultipleStep() {
        const isMultiple = Boolean(this.props.isMultiple);
        if (!isMultiple) {
            return {isMultiple: false, step: 1};
        }
        const step = parseFloat(this.props.saleMultipleQty || 1) || 1;
        return {isMultiple: true, step};
    },

    /**
     * Round up the quantity to the nearest step, with a minimum of 1 step.
     *
     * This matches "product page" behavior:
     * - no 0 here (configurator qty should not remove the product)
     * - always round UP when typing an arbitrary value
     */
    _roundUpToStep(qty, step) {
        const effectiveMin = Math.max(1, step);
        let v = parseFloat(qty || 0);

        if (!Number.isFinite(v) || v <= 0) {
            v = effectiveMin;
        }

        // -1e-9 prevents rounding artifacts when value is already a multiple.
        v = Math.ceil(v / step - 1e-9) * step;
        v = Math.max(v, effectiveMin);
        return v;
    },

    /**
     * "+" button behavior:
     * - non-multiple => standard flow
     * - multiple => +step
     *
     * @override
     */
    increaseQuantity() {
        const {isMultiple, step} = this._getMultipleStep();
        if (!isMultiple) {
            return super.increaseQuantity(...arguments);
        }
        const current = parseFloat(this.props.quantity || 0) || 0;
        const next = this._roundUpToStep(current + step, step);
        this.props.setQuantity(next);
    },

    /**
     * "-" button behavior:
     * - non-multiple => standard flow
     * - multiple => -step but never below effectiveMin (>= one step)
     *
     * @override
     */
    decreaseQuantity() {
        const {isMultiple, step} = this._getMultipleStep();
        if (!isMultiple) {
            return super.decreaseQuantity(...arguments);
        }
        const current = parseFloat(this.props.quantity || 0) || 0;
        const effectiveMin = Math.max(1, step);
        const nextRaw = current - step;
        const next = nextRaw <= effectiveMin ? effectiveMin : nextRaw;
        this.props.setQuantity(next);
    },

    /**
     * Manual input behavior (typing):
     * - non-multiple => standard flow
     * - multiple => round UP to step, then setQuantity
     *
     * @override
     */
    async setQuantity(event) {
        const {isMultiple, step} = this._getMultipleStep();
        if (!isMultiple) {
            return super.setQuantity(...arguments);
        }

        const inputQty = parseFloat(event.target.value);
        const rounded = this._roundUpToStep(inputQty, step);
        const didUpdateQuantity = await this.props.setQuantity(rounded);

        if (!didUpdateQuantity) {
            this.render();
        }
    },
});
