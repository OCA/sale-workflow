/** Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

export class SaleExceptionLineTooltipField extends Component {
    static template = "sale_exception_line_tooltip.SaleExceptionLineTooltipField";
    static props = standardFieldProps;
    static fieldDependencies = [{name: "exceptions_tooltip", type: "char"}];
}

export const saleExceptionLineTooltipField = {
    component: SaleExceptionLineTooltipField,
    fieldDependencies: SaleExceptionLineTooltipField.fieldDependencies,
    supportedTypes: ["boolean"],
};

registry
    .category("fields")
    .add("sale_exception_line_tooltip", saleExceptionLineTooltipField);
