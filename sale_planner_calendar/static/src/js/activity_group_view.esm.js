/** @odoo-module **/

import {registerPatch} from "@mail/model/model_core";
import {attr} from "@mail/model/model_field";

registerPatch({
    name: "ActivityGroup",
    modelMethods: {
        convertData(data) {
            const data2 = this._super(data);
            data2.is_planner = data.is_planner;
            return data2;
        },
    },
    fields: {
        is_planner: attr({default: false}),
    },
});

registerPatch({
    name: "ActivityGroupView",
    recordMethods: {
        onClickFilterButton(ev) {
            this._super(...arguments);
            const data = _.extend({}, $(ev.currentTarget).data(), $(ev.target).data());
            if (data.is_planner === 1) {
                this.env.services.orm
                    .call("res.users", "get_action_sale_planner_calendar_event")
                    .then((action) => {
                        action.domain = data.domain;
                        this.env.services.action.doAction(action);
                    });
            }
        },
    },
});
