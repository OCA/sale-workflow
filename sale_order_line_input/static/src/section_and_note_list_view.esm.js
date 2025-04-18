/** @odoo-module **/

import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";
import {ListRenderer} from "@web/views/list/list_renderer";
const {useEffect} = owl;

export class SOLSectionAndNoteListRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.titleField = "name";
        useEffect(
            () => this.focusToName(this.props.list.editedRecord),
            () => [this.props.list.editedRecord]
        );
    }

    focusToName(editRec) {
        if (editRec && editRec.isVirtual && this.isSectionOrNote(editRec)) {
            const col = this.state.columns.find((c) => c.name === this.titleField);
            this.focusCell(col, null);
        }
    }

    isSectionOrNote(record = null) {
        record = record || this.record;
        return ["line_section", "line_note"].includes(record.data.display_type);
    }

    getRowClass(record) {
        const existingClasses = super.getRowClass(record);
        return `${existingClasses} o_is_${record.data.display_type}`;
    }

    getCellClass(column, record) {
        const classNames = super.getCellClass(column, record);
        if (
            this.isSectionOrNote(record) &&
            column.widget !== "handle" &&
            column.name !== this.titleField
        ) {
            return `${classNames} o_hidden`;
        }
        return classNames;
    }

    getColumns(record) {
        const columns = super.getColumns(record);
        if (this.isSectionOrNote(record)) {
            return this.getSectionColumns(columns);
        }
        return columns;
    }

    getSectionColumns(columns) {
        const sectionCols = columns.filter(
            (col) =>
                col.widget === "handle" ||
                (col.type === "field" && col.name === this.titleField)
        );
        return sectionCols.map((col) => {
            if (col.name === this.titleField) {
                return {...col, colspan: columns.length - sectionCols.length + 1};
            }
            return {...col};
        });
    }
}
SOLSectionAndNoteListRenderer.template =
    "sale_order_line_input.sectionAndNoteListRenderer";

export const SOLSectionAndNoteView = {
    ...listView,
    Renderer: SOLSectionAndNoteListRenderer,
};
registry.category("views").add("sol_section_and_note", SOLSectionAndNoteView);
