/** @odoo-module */

import {Component, useEffect} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

function parseMatrix(matrix) {
    if (matrix) {
        const lines = matrix.split(/\r?\n/);
        const linesAndElement = lines.map((l) => l.split(";"));
        return {
            header: linesAndElement[0],
            lines: linesAndElement.slice(-(linesAndElement.length - 1)),
        };
    }
    else {
        return { header: false, lines: false };
    }
}

export class MatrixTableField extends Component {
    setup() {
        const {header, lines} = parseMatrix(this.props.value);
        this.headerElements = header;
        this.lines = lines;
        useEffect(() => {
            const {header, lines} = parseMatrix(this.props.value);
            this.headerElements = header;
            this.lines = lines;
        });
    }
}

MatrixTableField.template = "sale_mrp_bom_configurable.matrix";
MatrixTableField.props = {
    ...standardFieldProps,
};
MatrixTableField.supportedTypes = ["text"];

registry.category("fields").add("matrix_table", MatrixTableField);
