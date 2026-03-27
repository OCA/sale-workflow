/** @odoo-module **/
/* Copyright 2026 Tecnativa - Carlos Lopez
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {useEffect, useState} from "@odoo/owl";

import {useRecordObserver} from "@web/model/relational_model/utils";
import {SaleOrderLineProductField} from "@sale/js/sale_product_field";
import {
    ProductLabel,
    ProductLabelSectionAndNoteFieldAutocomplete,
    ProductLabelVisibilityButton,
    useIsNote,
    useIsSection,
} from "@web_widget_product_label_section_and_note/components/product_label_section_and_note_field/product_label_section_and_note_field.esm";
import {patch} from "@web/core/utils/patch";

patch(SaleOrderLineProductField.prototype, {
    setup() {
        super.setup();
        this.labelVisibility = useState({value: false});
        this.isProductVisible = useState({value: false});
        this.changeProductVisibility = true;
        this.columnIsProductAndLabel = useState({
            value: this.props.record.columnIsProductAndLabel,
        });

        useEffect(
            () => {
                this.columnIsProductAndLabel.value =
                    this.props.record.columnIsProductAndLabel;
            },
            () => [this.props.record.columnIsProductAndLabel]
        );

        useRecordObserver(async (record) => {
            if (this.changeProductVisibility) {
                const label = record.data.name || "";
                this.isProductVisible.value = label.includes(this.productName);
            }
        });
    },

    get productName() {
        return this.props.record.data[this.props.name][1];
    },

    get label() {
        let label = this.props.record.data.name || "";
        if (label.includes(this.productName)) {
            label = label.replace(this.productName, "");
            if (label.includes("\n")) {
                label = label.replace("\n", "");
            }
        }
        return label;
    },

    get isSectionOrNote() {
        return useIsSection(this.props.record) || useIsNote(this.props.record);
    },

    switchLabelVisibility() {
        this.labelVisibility.value = !this.labelVisibility.value;
    },

    switchProductVisibility() {
        let new_name = "";
        if (this.isProductVisible.value && this.productName) {
            new_name = this.label;
        } else {
            new_name = this.productName + "\n" + this.label;
        }
        this.props.record.update({name: new_name});
        this.isProductVisible.value = !this.isProductVisible.value;
    },

    updateLabel(value) {
        this.changeProductVisibility = false;
        this.props.record.update({
            name:
                this.productName &&
                this.productName !== value &&
                this.isProductVisible.value
                    ? `${this.productName}\n${value}`
                    : value,
        });
    },
});

SaleOrderLineProductField.components = {
    ...SaleOrderLineProductField.components,
    Many2XAutocomplete: ProductLabelSectionAndNoteFieldAutocomplete,
    ProductLabel: ProductLabel,
    ProductLabelVisibilityButton: ProductLabelVisibilityButton,
};
