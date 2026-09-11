import {ProductConfiguratorDialog} from "@sale/js/product_configurator_dialog/product_configurator_dialog";
import {patch} from "@web/core/utils/patch";

patch(ProductConfiguratorDialog, {
    props: {
        ...ProductConfiguratorDialog.props,
        saleOrderTypeId: {type: Number, optional: true},
    },
});

patch(ProductConfiguratorDialog.prototype, {
    _getAdditionalRpcParams() {
        return {
            ...super._getAdditionalRpcParams(),
            sale_order_type_id: this.props.saleOrderTypeId,
        };
    },
});
