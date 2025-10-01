/** @odoo-module **/

import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";
import {useAskRecurrenceUpdatePolicy} from "@calendar/views/ask_recurrence_update_policy_hook";

patch(ListController.prototype, "sale_planner_calendar.ListController", {
    setup() {
        this._super(...arguments);
        this.askRecurrenceUpdatePolicy = useAskRecurrenceUpdatePolicy();
    },
    async onDeleteSelectedRecords() {
        const _super = this._super.bind(this);
        const resIds = await this.model.root.getResIds(true);
        var records = this.model.root.records.filter((record) =>
            resIds.includes(record.resId)
        );
        if (
            this.props.context &&
            this.props.context.choose_unlink_method &&
            !records.some((record) => !record.data.recurrency)
        ) {
            const recurrenceUpdate = await this.askRecurrenceUpdatePolicy();
            if (recurrenceUpdate && recurrenceUpdate !== "self_only") {
                await this._launchMassDeletion(records, recurrenceUpdate);
                await this.model.load();
                return this.model.notify();
            } else if (recurrenceUpdate) {
                await this.model.root.deleteRecords();
                return this.model.notify();
            }
            return;
        }
        return _super(...arguments);
    },
    _launchMassDeletion: async function (records, recurrenceUpdate) {
        let recs = [...records];
        while (recs.length) {
            const record = recs[0];
            const recordsSameRecurrence = recs.filter(
                (rec) => rec.resId === record.resId
            );
            const event = recordsSameRecurrence.reduce((prev, curr) => {
                return prev.resId < curr.resId ? prev : curr;
            });
            await this.env.services.orm.call(
                this.props.resModel,
                "action_mass_deletion",
                [[event.resId], recurrenceUpdate]
            );
            recs = recs.filter((el) => !recordsSameRecurrence.includes(el));
        }
    },
});
