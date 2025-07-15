import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {Component} from "@odoo/owl";

export class MoveBaseWidget extends Component {
    static template = "sale_planner_calendar.MoveBaseWidget";
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.type = "none";
    }
    async onClickMove(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        const dataset = this.props.record.model.root.records;
        var index = dataset.indexOf(this.props.record);
        var timeUnit = -this.props.record.data.duration;
        var baseRecord = {};
        if (this.type === "previous") {
            if (index === 0) {
                return;
            }
            baseRecord = dataset[index - 1];
        } else if (this.type === "after") {
            if (index === dataset.length - 1) {
                return;
            }
            baseRecord = dataset[index + 1];
            timeUnit = baseRecord.data.duration;
        }
        await this.orm.write(this.props.record.resModel, [this.props.record.resId], {
            hour: baseRecord.data.hour + timeUnit,
        });
        this.props.record.model.load();
    }
}

export class MovePreviousWidget extends MoveBaseWidget {
    setup() {
        super.setup();
        this.type = "previous";
    }
}

export class MoveAfterWidget extends MoveBaseWidget {
    setup() {
        super.setup();
        this.type = "after";
    }
}

registry
    .category("view_widgets")
    .add("move_previous_record", {component: MovePreviousWidget});
registry
    .category("view_widgets")
    .add("move_after_record", {component: MoveAfterWidget});
