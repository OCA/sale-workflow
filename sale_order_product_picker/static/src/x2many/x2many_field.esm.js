/** @odoo-module **/
/* Copyright 2023 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
 */
import {X2ManyField} from "@web/views/fields/x2many/x2many_field";
import {patch} from "@web/core/utils/patch";
import {
    useActiveActions,
    useOpenX2ManyRecord,
    useX2ManyCrud,
} from "@web/views/fields/relational_utils";
patch(X2ManyField.prototype, "sale_order_product_picker.X2ManyField", {
    /**
     * We override the setup to intercept changes in the order lines, and in the event
     * that there are picker lines displayed, we will transfer these changes to the
     * picker.
     *
     * This is just used when opening line form.
     *
     * @override
     */
    setup() {
        this._super(...arguments);
        if (
            this.field.relation === "sale.order.picker" ||
            (this.field.relation === "sale.order.line" &&
                "picker_ids" in this.props.record.model.root.data)
        ) {
            const lineList = this.props.record.model.root.data.order_line;
            const {saveRecord, updateRecord, removeRecord} = useX2ManyCrud(
                () => lineList,
                false
            );
            const newSaveRecord = async (object) => {
                // Function used when creating a new record.
                const res = await saveRecord(object);
                const picker_record = this.props.record.data.picker_ids.records.filter(
                    (pickRecord) =>
                        JSON.stringify(pickRecord.data.product_id) ===
                        JSON.stringify(object.data.product_id)
                )[0];
                if (picker_record) {
                    picker_record.update({
                        product_uom_qty:
                            picker_record.data.product_uom_qty +
                            object.data.product_uom_qty,
                        is_in_order: true,
                    });
                }
                return res;
            };
            const newUpdateRecord = (record) => {
                // Function used when updating a record.
                const res = updateRecord(record);
                const last_qty = lineList.records.filter(
                    (r) => r.__bm_handle__ === record.__bm_handle__
                )[0].data.product_uom_qty;
                const picker_record = this.props.record.data.picker_ids.records.filter(
                    (pickRecord) =>
                        JSON.stringify(pickRecord.data.product_id) ===
                        JSON.stringify(record.data.product_id)
                )[0];
                if (picker_record) {
                    const diff_qty = record.data.product_uom_qty - last_qty;
                    picker_record.update({
                        product_uom_qty: picker_record.data.product_uom_qty + diff_qty,
                        is_in_order: Boolean(
                            picker_record.data.product_uom_qty + diff_qty
                        ),
                    });
                }
                return res;
            };
            const newRemoveRecord = (record) => {
                // Function used when removing a record.
                const res = removeRecord(record);
                const last_qty = lineList.records.filter(
                    (r) => r.__bm_handle__ === record.__bm_handle__
                )[0].data.product_uom_qty;
                const picker_record = this.props.record.data.picker_ids.records.filter(
                    (pickRecord) =>
                        JSON.stringify(pickRecord.data.product_id) ===
                        JSON.stringify(record.data.product_id)
                )[0];
                if (picker_record) {
                    picker_record.update({
                        product_uom_qty: picker_record.data.product_uom_qty - last_qty,
                        is_in_order: Boolean(
                            picker_record.data.product_uom_qty - last_qty
                        ),
                    });
                }
                return res;
            };
            const activeField = this.props.record.model.root.activeFields.order_line;
            const subViewActiveActions =
                activeField.views[activeField.viewMode].activeActions;
            const activeActions = useActiveActions({
                crudOptions: Object.assign({}, activeField.options, {
                    onDelete: newRemoveRecord,
                }),
                fieldType: "one2many",
                subViewActiveActions,
                getEvalParams: (props) => {
                    return {
                        evalContext: props.record.evalContext,
                        readonly: false,
                    };
                },
            });
            const openRecord = useOpenX2ManyRecord({
                resModel: lineList.resModel,
                activeField: activeField,
                activeActions: activeActions,
                getList: () => lineList,
                saveRecord: newSaveRecord,
                updateRecord: newUpdateRecord,
                withParentId: true,
            });
            this._openRecord = (params) => {
                const activeElement = document.activeElement;
                const delay = this.props.decorations.delay_open || 0;
                setTimeout(openRecord, delay, {
                    ...params,
                    onClose: () => {
                        if (activeElement) {
                            activeElement.focus();
                        }
                    },
                });
            };
        }
    },

    async openRecord(record, context) {
        if (this.field.relation === "sale.order.picker") {
            return this._openRecord({record, mode: "edit", context});
        }
        return this._super(...arguments);
    },
});
