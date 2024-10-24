/** @odoo-module **/
/* Copyright 2024 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
 */
export class PickerChangeProcessor {
    constructor(waitTime, x2mList, $pickerKanban) {
        this.waitTime = waitTime * 1000;
        this.changes = {};
        this.timeoutId = null;
        this.x2mList = x2mList;
        this.$pickerKanban = $pickerKanban;
    }

    addChange(change) {
        if (!this.changes[change.id]) {
            this.changes[change.id] = {
                qty: 0,
                pickerRecord: change.pickerRecord,
                ctx: change.ctx,
                orderLines: change.orderLines,
            };
        }
        this.changes[change.id].qty++;
        this.resetTimer();
    }

    resetTimer() {
        if (this.timeoutId !== null) {
            clearTimeout(this.timeoutId);
        }
        this.timeoutId = setTimeout(() => this.processChanges(), this.waitTime);
    }

    processChanges() {
        if (Object.keys(this.changes).length <= 0) {
            return;
        }
        this.$pickerKanban.prepend("<div id='processing_picker'/>");
        const lineChanges = [];
        for (var key in this.changes) {
            var change = this.changes[key];
            if (!change.orderLines.length) {
                var ctx = change.ctx;
                Object.assign(ctx, {
                    default_product_uom_qty:
                        change.qty * change.pickerRecord.data.unit_factor,
                });
                lineChanges.push({
                    operation: "CREATE",
                    editable: "bottom",
                    context: [ctx],
                });
            } else {
                const pickedRecord = change.orderLines[0];
                const data = {};
                Object.assign(data, {
                    product_uom_qty:
                        pickedRecord.data.product_uom_qty +
                        change.qty * change.pickerRecord.data.unit_factor,
                });
                lineChanges.push({
                    operation: "UPDATE",
                    id: pickedRecord.__bm_handle__,
                    data,
                });
            }
        }
        const parentID =
            this.x2mList.model.__bm__.localData[this.x2mList.__bm_handle__].parentID;
        this.x2mList.model.__bm__
            .notifyChanges(parentID, {
                order_line: {
                    operation: "MULTI",
                    commands: lineChanges,
                },
            })
            .then(async () => {
                this.x2mList.model.root.__syncData();
                this.x2mList.model.notify();
                const pickerChanges = [];
                for (var key in this.changes) {
                    const change = this.changes[key];
                    const orderLine = this.x2mList.records.filter(
                        (line) =>
                            line.data.product_id[0] ===
                            change.pickerRecord.data.product_id[0]
                    )[0];
                    pickerChanges.push({
                        operation: "UPDATE",
                        record: change.pickerRecord,
                        data: {
                            to_process: false,
                            is_in_order: true,
                            line_price_reduce: orderLine.data.price_reduce,
                            discount: orderLine.data.discount,
                        },
                    });
                }
                await this.x2mList.applyCommands("picker_ids", pickerChanges);
                this.changes = {};
                this.$pickerKanban.find("#processing_picker").remove();
            });
    }
}
