/** @odoo-module **/

import {ActivityMenu} from "@mail/core/web/activity_menu";
import {patch} from "@web/core/utils/patch";

patch(ActivityMenu.prototype, {
    openActivityGroup(group, filter = "all") {
        if (group.model === "calendar.event" && group.is_planner) {
            this.dropdown.close();
            const context = {
                search_default_my_event_planner: 1,
                search_default_state_pending: 1,
                search_default_planner_today: 0,
            };
            if (filter === "my") {
                context.search_default_planner_overdue = 1;
                context.search_default_planner_today = 1;
            } else {
                context["search_default_planner_" + filter] = 1;
            }
            this.action.doAction(
                "sale_planner_calendar.action_sale_planner_calendar_event",
                {
                    additionalContext: context,
                    clearBreadcrumbs: true,
                }
            );
        } else {
            super.openActivityGroup(...arguments);
        }
    },
});
