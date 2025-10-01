/** @odoo-module **/

import {ListController} from "@web/views/list/list_controller";
import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class SalePlannerCalendarEventListController extends ListController {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");
    }
    async onClickNewSaleOrder() {
        console.log(this);
        const calendar_summary_id = this.props.context.default_calendar_summary_id;
        const action = await this.orm.call(
            "calendar.event",
            "action_open_sale_order",
            [false, {new_order: true}],
            {context: {calendar_summary_id: calendar_summary_id || false}}
        );
        this.action.doAction(action);
    }
}

export const SalePlannerCalendarEventListView = {
    ...listView,
    Controller: SalePlannerCalendarEventListController,
    buttonTemplate: "SalePlannerCalendarEventListView.buttons",
};

registry
    .category("views")
    .add("sale_planner_calendar_event_tree", SalePlannerCalendarEventListView);
