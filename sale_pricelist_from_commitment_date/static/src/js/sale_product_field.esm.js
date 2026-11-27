import {ComboConfiguratorDialog} from "@sale/js/combo_configurator_dialog/combo_configurator_dialog";
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

// The combo configurator dialog takes the order date as `date`, not `soDate`,
// and passes it on to its price RPC and to the nested product configurator.
patch(ComboConfiguratorDialog, {
    props: {...ComboConfiguratorDialog.props, soDate: {type: String, optional: true}},
});

patch(ComboConfiguratorDialog.prototype, {
    _getAdditionalRpcParams() {
        const params = super._getAdditionalRpcParams();
        if (this.props.soDate) {
            params.date = this.props.soDate;
        }
        return params;
    },

    _getAdditionalDialogProps() {
        const props = super._getAdditionalDialogProps();
        if (this.props.soDate) {
            props.soDate = this.props.soDate;
        }
        return props;
    },
});
