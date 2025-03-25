import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {ListRenderer} from "@web/views/list/list_renderer";
import {patch} from "@web/core/utils/patch";

patch(ListRenderer.prototype, {
    get canCreate() {
        const parentRecord = this.props.list.model.root;
        const disableAddingLines = parentRecord?.data?.disable_adding_lines;
        return !disableAddingLines && super.canCreate;
    },
});

patch(KanbanRenderer.prototype, {
    get canCreate() {
        const parent = this.props.list.model.root;
        const parentModel = parent?.resModel || parent?.model;
        const fieldName = this.props.arch.attrs.name;

        if (parentModel === "sale.order" && fieldName === "order_line") {
            const disabled = parent.data?.disable_adding_lines;
            return !disabled && super.canCreate;
        }

        return super.canCreate;
    },
});
