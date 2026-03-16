import {SaleOrderLineProductField} from "@sale/js/sale_product_field";
import {patch} from "@web/core/utils/patch";
import {serializeDateTime} from "@web/core/l10n/dates";

patch(SaleOrderLineProductField.prototype, {
    _getCommitmentDateSerialized() {
        const commitmentDate = this.props.record.model.root.data.commitment_date;
        return commitmentDate ? serializeDateTime(commitmentDate) : null;
    },

    _getAdditionalDialogProps() {
        const props = super._getAdditionalDialogProps();
        const date = this._getCommitmentDateSerialized();
        if (date) {
            props.soDate = date;
            props.date = date;
        }
        return props;
    },

    _getAdditionalRpcParams() {
        const params = super._getAdditionalRpcParams();
        const date = this._getCommitmentDateSerialized();
        if (date) {
            params.date = date;
        }
        return params;
    },
});
