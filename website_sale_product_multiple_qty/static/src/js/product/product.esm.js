import {Product} from "@sale/js/product/product";
import {patch} from "@web/core/utils/patch";

/**
 * Extend the Product component props so the configurator/product templates
 * can pass variant-level "sale multiple" information.
 *
 * This is used by QuantityButtons to enforce step logic.
 */
patch(Product, {
    props: {
        ...Product.props,
        is_multiple: {type: Number, optional: true},
        sale_multiple_qty: {type: Number, optional: true},
    },
});
