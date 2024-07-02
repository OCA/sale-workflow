/** @odoo-module **/
/* Copyright 2024 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
 */
import {_lt} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";
import {FormController} from "@web/views/form/form_controller";
import {useService} from "@web/core/utils/hooks";

patch(FormController.prototype, "sale_order_product_picker.FormController", {
    setup() {
        this._super(...arguments);
        this.notification = useService("notification");
    },
    checkIsProcessingPicker() {
        const data = this.model.root.data;
        if (data && data.picker_ids) {
            const recordsToProcess = data.picker_ids.records.filter((record) => {
                return record.data.to_process;
            });
            if (recordsToProcess.length > 0) {
                this.notification.add(
                    _lt("You must wait for the picker lines to be written"),
                    {
                        type: "danger",
                    }
                );
                return true;
            }
        }
        return false;
    },
    async beforeLeave() {
        if (this.checkIsProcessingPicker()) {
            return Promise.reject();
        }
        return this._super(...arguments);
    },
    async saveButtonClicked() {
        if (this.checkIsProcessingPicker()) {
            return Promise.reject();
        }
        return this._super(...arguments);
    },
});
