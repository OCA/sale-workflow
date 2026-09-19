/** @odoo-module **/
/*
    Copyright 2026 Solvos
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
*/

import {SectionAndNoteListRenderer} from "@account/components/section_and_note_fields_backend/section_and_note_fields_backend";
import {patch} from "@web/core/utils/patch";

patch(SectionAndNoteListRenderer.prototype, {
    hideDescription(column, record, classNames) {
        if (
            column.name === "name" &&
            !record.data.display_type &&
            this.props.list.resModel === "sale.order.line"
        ) {
            return classNames + " o_hidden";
        }
        return classNames;
    },

    getCellClass(column, record) {
        let classNames = super.getCellClass(column, record);
        classNames = this.hideDescription(column, record, classNames);
        return classNames;
    },
});
