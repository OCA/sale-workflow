/** @odoo-module **/
/* Copyright 2023 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
 */
import {Component, useSubEnv, xml} from "@odoo/owl";

import {Dialog} from "@web/core/dialog/dialog";
import {KanbanRecord} from "@web/views/kanban/kanban_record";
import {X2ManyField} from "@web/views/fields/x2many/x2many_field";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

/**
 * Dialog used to show the images of products bigger than showed on kanban
 */
export class ImageDialog extends Component {}
ImageDialog.components = {Dialog};
ImageDialog.template = xml`
<Dialog footer="false" title="props.product_id[1]">
    <div class="form-text text-center">
        <img t-att-src="'/web/image/product.product/' + props.product_id[0] + '/image_1920'" style="max-width: 100%; object-fit: contain;" alt="Product image"/>
    </div>
</Dialog>`;

/**
 * Dialog used to select the line that want to modify
 */
export class PickerMultiLineDialog extends Component {
    setup() {
        const {x2mList, orderLines, config} = this.props;
        useSubEnv({config});
        x2mList.records = orderLines;
        this.field_props = {
            record: x2mList.model.root,
            name: "order_line",
            value: x2mList,
            readonly: false,
            decorations: {delay_open: 50},
        };
    }
}
PickerMultiLineDialog.components = {Dialog, X2ManyField};
PickerMultiLineDialog.template = xml`
<Dialog footer="false" title="'Select the line that you want to edit'">
    <div class="form-text">
        <X2ManyField t-props="field_props" t-on-click="props.close"/>
    </div>
</Dialog>`;

patch(KanbanRecord.prototype, "sale_order_product_picker.KanbanRecord", {
    setup() {
        this._super(...arguments);
        this.dialogs = useService("dialog");
        this.disableGlobalClick = false;
    },
    defaultFields() {
        return ["product_id", "price_unit"];
    },
    contextPicker() {
        var ctx = {};
        for (var field of this.defaultFields()) {
            if (field in this.props.record.data) {
                var key = "default_" + field;
                ctx[key] =
                    this.props.record.data[field][0] || this.props.record.data[field];
            }
        }
        return ctx;
    },
    /**
     * When a KanbanRecord is clicked anywhere inside the card with the class
     * `o_picker_kanban`, the method open record has to open the created record on
     * lines, or create a new one if it does not exist.
     *
     * It also allows to click on buttons to quick add and duplicate lines.
     *
     * @override
     * @private
     */
    async onGlobalClick(ev) {
        if (this.disableGlobalClick) {
            return;
        }
        var $kanban = $(ev.currentTarget).closest(".o_picker_kanban");
        if ($(ev.target).closest(".o_picker_quick_add").length) {
            // Quick add clicked
            this._onQuickAddClicked();
        } else if ($(ev.target).closest(".o_picker_form_add").length) {
            // Duplicate line clicked
            this._onFormAddClicked();
        } else if ($(ev.target).closest(".o_picker_img_full_size").length) {
            // Duplicate line clicked
            this._openImageFullResolution();
        } else if ($kanban.length) {
            // General click
            this._openRecordPickerForm();
        } else {
            // Normal sequence
            this._super.apply(this, arguments);
        }
    },
    /**
     * Open or add record with form.
     *
     * @private
     */
    async _openRecordPickerForm() {
        const {openRecord, record} = this.props;
        var ctx = this.contextPicker();
        const x2mList = record.model.root.data.order_line;
        const orderLines = x2mList.records.filter(
            (line) => line.data.product_id[0] === record.data.product_id[0]
        );
        if (!orderLines.length) {
            openRecord(null, ctx);
        } else if (orderLines.length === 1) {
            const pickedRecord = orderLines[0];
            openRecord(pickedRecord);
        } else {
            this._openMultiLineModalPicker(x2mList, orderLines);
        }
    },
    /**
     * Add a record quickly to lines.
     *
     * @private
     */
    async _onQuickAddClicked() {
        const {record} = this.props;
        var ctx = this.contextPicker();
        const x2mList = record.model.root.data.order_line;
        const orderLines = x2mList.records.filter(
            (line) => line.data.product_id[0] === record.data.product_id[0]
        );
        this.disableGlobalClick = true;
        if (!orderLines.length) {
            // Disable global click to avoid actions while record is added
            const lineRec = await x2mList.addNew({
                position: "bottom",
                context: ctx,
            });
            record.update({
                product_uom_qty:
                    record.data.product_uom_qty + lineRec.data.product_uom_qty,
                is_in_order: true,
            });
        } else if (orderLines.length === 1) {
            const pickedRecord = orderLines[0];
            const last_qty = pickedRecord.data.product_uom_qty;
            const field = pickedRecord.data.secondary_uom_id
                ? "secondary_uom_qty"
                : "product_uom_qty";
            await x2mList.applyCommands("order_line", [
                {
                    operation: "UPDATE",
                    record: pickedRecord,
                    data: {[field]: pickedRecord.data[field] + 1},
                },
            ]);
            const diff_qty = pickedRecord.data.product_uom_qty - last_qty;
            record.update({product_uom_qty: record.data.product_uom_qty + diff_qty});
        } else {
            this._openMultiLineModalPicker(x2mList, orderLines);
        }
        this.disableGlobalClick = false;
    },
    /**
     * Add new record using form to lines.
     *
     * @private
     */
    _onFormAddClicked() {
        const {openRecord} = this.props;
        var ctx = this.contextPicker();
        openRecord(null, ctx);
    },
    /**
     * Open lines selector modal to select the line that want to modify.
     *
     * @private
     * @param {Object} x2mList
     * @param {Array} orderLines
     */
    _openMultiLineModalPicker(x2mList, orderLines) {
        const recordsBackup = x2mList.records;
        this.dialogs.add(
            PickerMultiLineDialog,
            {
                x2mList,
                orderLines,
                config: this.env.config,
            },
            {
                onClose: () => {
                    x2mList.records = recordsBackup;
                },
            }
        );
    },
    /**
     * Open image of product in a modal with full resolution size.
     *
     * @private
     */
    _openImageFullResolution() {
        const product_id = this.props.record.data.product_id;
        this.dialogs.add(ImageDialog, {
            product_id,
        });
    },
});
