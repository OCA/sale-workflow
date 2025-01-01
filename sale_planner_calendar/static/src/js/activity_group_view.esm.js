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
                const context = {};
                if (data.filter === "my") {
                    context.search_default_planner_overdue = 1;
                    context.search_default_planner_today = 1;
                } else {
                    context["search_default_planner_" + data.filter] = 1;
                }
                this.env.services.orm
                    .call("res.users", "get_action_sale_planner_calendar_event")
                    .then((action) => {
                        action.domain = data.domain;
                        const action_ctx = JSON.parse(
                            action.context.replace(/'/g, '"')
                        );
                        action.context = {...action_ctx, ...context};
                        delete action.context.search_default_my_event_planner;
                        this.env.services.action.doAction(action, {
                            clearBreadcrumbs: true,
                        });
                    });
            }
        },
    },
});
