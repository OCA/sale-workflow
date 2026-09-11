import {SaleOrderLineProductField} from "@sale/js/sale_product_field";
import {patch} from "@web/core/utils/patch";

patch(SaleOrderLineProductField.prototype, {
    _getAdditionalDialogProps() {
        return {
            ...super._getAdditionalDialogProps(),
            saleOrderTypeId: this.props.record.model.root.data.type_id?.[0],
        };
    },
});
