/** @odoo-module **/
import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";

function shouldCreateStore() {
    return this.props.context.configurable_quotation === 1;
}

function createRecord() {
    if (shouldCreateStore.call(this)) {
        this.actionService.doAction(
            "sale_mrp_bom_configurable.action_create_quotations_configurable"
        );
    } else {
        this._super(...arguments);
    }
}

patch(ListController.prototype, "Add new configurable quotations action in list", {
    async createRecord() {
        createRecord.call(this);
    },
});
