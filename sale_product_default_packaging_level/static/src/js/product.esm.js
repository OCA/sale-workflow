import {patch} from "@web/core/utils/patch";
import {Product} from "@sale/js/product/product";

patch(Product, {
    props: {
        ...Product.props,
        default_product_packaging_level_name: {type: String, optional: true},
    },
});
