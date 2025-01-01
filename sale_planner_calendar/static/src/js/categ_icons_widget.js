/** @odoo-module **/
import {registry} from "@web/core/registry";
import {Component} from "@odoo/owl";

class CategIconsWidget extends Component {
    setup() {
        const categIcons = this.props.record.data.categ_icons;
        this.iconList = categIcons ? categIcons.split(",") : [];
    }
}

CategIconsWidget.template = "sale_planner_calendar.CategIconsWidget";

registry.category("fields").add("categ_icons_widget", CategIconsWidget);
export default CategIconsWidget;
