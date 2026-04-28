import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";

class CategIconsWidget extends Component {
    static template = "sale_planner_calendar.CategIconsWidget";
    setup() {
        const categIcons = this.props.record.data.categ_icons;
        this.iconList = categIcons ? categIcons.split(",") : [];
    }
}
const CategIconsWidgetField = {
    component: CategIconsWidget,
};
registry.category("fields").add("categ_icons_widget", CategIconsWidgetField);
