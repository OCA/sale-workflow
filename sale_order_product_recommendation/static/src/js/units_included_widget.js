odoo.define(
    "sale_order_product_recommendation.units_included_widget",
    function (require) {
        "use strict";

        const AbstractField = require("web.AbstractField");
        const fieldRegistry = require("web.field_registry");
        const {formatFloat} = require("@web/fields/formatters");

        const UnitsIncludedWidget = AbstractField.extend({
            template: "sale_order_product_recommendation.units_included_widget",
            supportedFieldTypes: ["float", "integer"],

            events: {
                "click .o_units_included_widget_minus": "_onClickMinus",
                "click .o_units_included_widget_plus": "_onClickPlus",
                "change .o_product_widget_input": "_onChangeInput",
                "focus .o_product_widget_input": "_onInputFocus",
            },

            _updateValue: function (value) {
                const updatedValue = parseFloat(value) >= 0 ? parseFloat(value) : 0;
                this._setValue(formatFloat(updatedValue));
            },

            _onClickMinus: function () {
                this._updateValue(this.value - 1);
            },

            _onClickPlus: function () {
                this._updateValue(this.value + 1);
            },

            _onChangeInput: function (ev) {
                this._updateValue(ev.target.value);
            },

            _onInputFocus: function (ev) {
                ev.target.select();
            },
        });

        fieldRegistry.add("units_included_widget", UnitsIncludedWidget);

        return UnitsIncludedWidget;
    }
);
