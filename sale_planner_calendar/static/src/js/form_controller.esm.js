/** @odoo-module **/

import {FormController} from "@web/views/form/form_controller";
import {patch} from "@web/core/utils/patch";
import {useAskRecurrenceUpdatePolicy} from "@calendar/views/ask_recurrence_update_policy_hook";

patch(FormController.prototype, "sale_planner_calendar.FormController", {
    setup() {
        this._super(...arguments);
        this.askRecurrenceUpdatePolicy = useAskRecurrenceUpdatePolicy();
    },
    async deleteRecord() {
        const _super = this._super.bind(this);
        var record = this.model.root.data;
        if (
            this.props.context &&
            this.props.context.choose_unlink_method &&
            record.recurrency
        ) {
            const recurrenceUpdate = await this.askRecurrenceUpdatePolicy();
            if (recurrenceUpdate && recurrenceUpdate !== "self_only") {
                await this._launchMassDeletion(record, recurrenceUpdate);
                return this.env.config.historyBack();
            } else if (recurrenceUpdate) {
                await this.model.root.delete();
                return this.env.config.historyBack();
            }
            return;
        }
        return _super(...arguments);
    },
    _launchMassDeletion: async function (record, recurrenceUpdate) {
        const resId = record.id;
        await this.env.services.orm.call(this.props.resModel, "action_mass_deletion", [
            [resId],
            recurrenceUpdate,
        ]);
    },
});
