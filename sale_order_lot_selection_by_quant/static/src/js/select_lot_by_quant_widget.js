odoo.define("sale_order_lot_selection_by_quant.select_lot_by_quant_widget", function (
    require
) {
    "use strict";

    var relationalFields = require("web.relational_fields");
    var FieldsRegistry = require("web.field_registry");
    var core = require("web.core");
    var _t = core._t;

    var SelectLotByQuantWidget = relationalFields.FieldMany2One.extend({
        resetOnAnyFieldChange: true,
        events: _.extend({}, relationalFields.FieldMany2One.prototype.events, {
            "click .o_select_lot_by_quant": "_onSelectLotByQuantBtn",
        }),

        /**
         * @override
         */
        _render: function () {
            const res = this._super.apply(this, arguments);
            this._renderSelectLotByQuantButton();
            return res;
        },

        /**
         * Show edit button (in Edit Mode) after the dropdown
         */
        _renderSelectLotByQuantButton: function () {
            this.$el.addClass("o_select_lot_by_quant_widget");
            const btn = this.$(".o_select_lot_by_quant");
            const dropdown = this.$(".o_input_dropdown");
            if (
                this.mode === "edit" &&
                dropdown.length !== 0 &&
                this.record.data.product_id.id
            ) {
                if (btn.length === 0) {
                    var $editConfigurationButton = $("<button>", {
                        type: "button",
                        class: "fa fa-search btn btn-secondary o_select_lot_by_quant",
                        tabindex: "-1",
                        draggable: false,
                        "aria-label": _t("Select Lot by Location"),
                        title: _t("Select Lot by Location"),
                    });
                    dropdown.append($editConfigurationButton);
                } else {
                    btn.show();
                }
            } else {
                btn.hide();
            }
            if (this.__parentedParent._onResize) {
                const parent = this.__parentedParent;
                const columns = parent.columns;
                // This check avoids an error that happens when
                // a new column is inserted in the table but
                // it's not rendered yet, so it doesn't have a <th> yet
                // so resizing at this point fails
                if (columns && columns.every(parent._getColumnHeader.bind(parent))) {
                    parent._onResize();
                }
            }
        },

        /**
         * @override
         * @param {Record} record
         * @param {OdooEvent} ev
         * @private
         */
        reset: async function (record, ev) {
            await this._super(...arguments);
            if (ev && ev.data.changes && ev.data.changes.product_id) {
                this._renderSelectLotByQuantButton();
            }
        },

        /**
         * Triggered on click of the button.
         * It is only shown in Edit mode,
         *
         * @private
         */
        _onSelectLotByQuantBtn: function () {
            const self = this;
            const dataPointID = self.record.id;
            const product_res_id = self.record.data.product_id.res_id || 0;
            const company_res_id = self.record.data.company_id.res_id;
            self.do_action(
                "sale_order_lot_selection_by_quant.action_select_lot_by_location",
                {
                    additional_context: {
                        default_product_id: product_res_id,
                        default_company_id: company_res_id,
                    },
                    on_close: function (result) {
                        if (result && result.changes) {
                            self.trigger_up("field_changed", {
                                dataPointID: dataPointID,
                                changes: result.changes,
                            });
                        }
                    },
                }
            );
        },
    });

    FieldsRegistry.add("select_lot_by_quant", SelectLotByQuantWidget);

    return SelectLotByQuantWidget;
});
