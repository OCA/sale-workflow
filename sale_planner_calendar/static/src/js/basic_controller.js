odoo.define("sale_planner_calendar.basic_controller", function (require) {
    "use strict";
    var BasicController = require("web.BasicController");
    var Dialog = require("web.Dialog");
    var core = require("web.core");

    var _t = core._t;
    var QWeb = core.qweb;

    BasicController.include({
        _launchMassDeletion: async function (records, recurrenceUpdate) {
            const localData = this.model.localData;
            while (records.length) {
                const record = records[0];
                const recordsSameRecurrence = records.filter(
                    (rec) =>
                        localData[rec.data.recurrence_id].data.id ===
                        localData[record.data.recurrence_id].data.id
                );
                const event = recordsSameRecurrence.reduce((prev, curr) => {
                    return prev.data.id < curr.data.id ? prev : curr;
                });
                await this._rpc({
                    model: this.modelName,
                    method: "action_mass_deletion",
                    args: [[event.data.id], recurrenceUpdate],
                });
                records = records.filter((el) => !recordsSameRecurrence.includes(el));
            }
        },
        _askRecurrenceUpdatePolicy: function () {
            return new Promise((resolve) => {
                new Dialog(this, {
                    title: _t("Edit Recurrent event"),
                    size: "small",
                    $content: $(QWeb.render("calendar.RecurrentEventUpdate")),
                    buttons: [
                        {
                            text: _t("Confirm"),
                            classes: "btn-primary",
                            close: true,
                            click: function () {
                                resolve(this.$("input:checked").val());
                            },
                        },
                    ],
                }).open();
            });
        },
        _deleteRecords: async function (ids) {
            const _super = this._super.bind(this);
            var records = _.map(ids, (id) => this.model.localData[id]);
            if (
                "choose_unlink_method" in this.initialState.getContext() &&
                !records.some((record) => !record.data.recurrency)
            ) {
                const recurrenceUpdate = await this._askRecurrenceUpdatePolicy();
                if (recurrenceUpdate !== "self_only") {
                    await this._launchMassDeletion(records, recurrenceUpdate);
                    if (this.controlPanelProps.view.arch.tag === "form") {
                        return this.trigger_up("history_back");
                    }
                    return this.reload();
                }
                this.confirmOnDelete = false;
            }
            return _super(...arguments);
        },
    });
});
