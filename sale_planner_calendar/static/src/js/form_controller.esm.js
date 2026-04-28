import {FormController} from "@web/views/form/form_controller";
import {patch} from "@web/core/utils/patch";
import {useAskRecurrenceUpdatePolicy} from "@calendar/views/ask_recurrence_update_policy_hook";

patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.askRecurrenceUpdatePolicy = useAskRecurrenceUpdatePolicy();
    },
    async deleteRecord() {
        var record = this.model.root.data;
        if (
            this.props.resModel === "calendar.event" &&
            this.props.context.choose_unlink_method &&
            record.recurrency
        ) {
            const recurrenceUpdate = await this.askRecurrenceUpdatePolicy();
            if (recurrenceUpdate && recurrenceUpdate !== "self_only") {
                await this._launchMassDeletion(recurrenceUpdate);
                return this.env.config.historyBack();
            } else if (recurrenceUpdate) {
                await this.model.root.delete();
                return this.env.config.historyBack();
            }
            return;
        }
        return super.deleteRecord(...arguments);
    },
    _launchMassDeletion: async function (recurrenceUpdate) {
        await this.env.services.orm.call(this.props.resModel, "action_mass_deletion", [
            [this.props.resId],
            recurrenceUpdate,
        ]);
    },
});
