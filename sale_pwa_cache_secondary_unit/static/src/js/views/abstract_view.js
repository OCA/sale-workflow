// Copyright 2021 Tecnativa - Alexandre Díaz
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
odoo.define("sale_pwa_cache_secondary_unit.AbstractView", function(require) {
    "use strict";

    require("web_widget_one2many_product_picker_sale_secondary_unit.AbstractView");
    const AbstractView = require("web.AbstractView");

    /**
     * Helper function to create field view definitions
     *
     * @private
     * @param {Object} params
     * @returns {Object}
     */
    function _constructFakeFieldDef(params) {
        return _.extend(
            {
                change_default: false,
                company_dependent: false,
                manual: false,
                views: {},
                searchable: true,
                store: false,
                readonly: true,
                required: false,
                sortable: false,
            },
            params
        );
    }

    /**
     * This is pure hard-coded magic. Adds new fields to the widget form view.
     */
    AbstractView.include({
        _injectSaleSecondaryUnitFields: function(viewInfo) {
            this._super.apply(this, arguments);
            const to_inject = {
                uom_factor: _constructFakeFieldDef({
                    type: "float",
                    depends: ["product_uom.factor"],
                    digits: 0,
                    group_operator: "sum",
                    manual: false,
                    readonly: true,
                    related: ["product_uom", "factor"],
                    required: false,
                    searchable: true,
                    sortable: false,
                    store: false,
                }),
                uom_rounding: _constructFakeFieldDef({
                    type: "float",
                    depends: ["product_uom.rounding"],
                    digits: 0,
                    group_operator: "sum",
                    manual: false,
                    readonly: true,
                    related: ["product_uom", "rounding"],
                    required: false,
                    searchable: true,
                    sortable: false,
                    store: false,
                }),
                secondary_uom_factor: _constructFakeFieldDef({
                    type: "float",
                    depends: ["secondary_uom_id.factor"],
                    digits: 0,
                    group_operator: "sum",
                    manual: false,
                    readonly: true,
                    related: ["secondary_uom_id", "factor"],
                    required: false,
                    searchable: true,
                    sortable: false,
                    store: false,
                }),
                secondary_uom_rounding: _constructFakeFieldDef({
                    type: "float",
                    depends: ["secondary_uom_id.uom_id.rounding"],
                    digits: 0,
                    group_operator: "sum",
                    manual: false,
                    readonly: true,
                    related: ["secondary_uom_id", "uom_id", "rounding"],
                    required: false,
                    searchable: true,
                    sortable: false,
                    store: false,
                }),
                secondary_uom_product_variant_ids: _constructFakeFieldDef({
                    type: "one2many",
                    context: {},
                    depends: ["secondary_uom_id.product_tmpl_id.product_variant_ids"],
                    domain: [],
                    manual: false,
                    readonly: true,
                    related: [
                        "secondary_uom_id",
                        "product_tmpl_id",
                        "product_variant_ids",
                    ],
                    relation: "product.product",
                    required: false,
                    searchable: true,
                    sortable: false,
                    store: false,
                }),
            };
            viewInfo.viewFields.order_line.views.form.fields = _.extend(
                {},
                to_inject,
                viewInfo.viewFields.order_line.views.form.fields
            );

            // Add fields to arch
            const $arch = $(viewInfo.viewFields.order_line.views.form.arch);

            // Add uom_factor?
            let $field = $arch.find("field[name='uom_factor']");
            if (!$field.length) {
                $("<FIELD/>", {
                    name: "uom_factor",
                    invisible: 1,
                    modifiers: '{"invisible": true, "readonly": true}',
                }).prependTo($arch);
            }
            // Add uom_rounding?
            $field = $arch.find("field[name='uom_rounding']");
            if (!$field.length) {
                $("<FIELD/>", {
                    name: "uom_rounding",
                    invisible: 1,
                    modifiers: '{"invisible": true, "readonly": true}',
                }).prependTo($arch);
            }
            // Add product_id_secondary_uom_ids?
            $field = $arch.find("field[name='secondary_uom_factor']");
            if (!$field.length) {
                $("<FIELD/>", {
                    name: "secondary_uom_factor",
                    invisible: 1,
                    modifiers: '{"invisible": true, "readonly": true}',
                }).prependTo($arch);
            }
            // Add secondary_uom_rounding?
            $field = $arch.find("field[name='secondary_uom_rounding']");
            if (!$field.length) {
                $("<FIELD/>", {
                    name: "secondary_uom_rounding",
                    invisible: 1,
                    modifiers: '{"invisible": true, "readonly": true}',
                }).prependTo($arch);
            }
            // Add secondary_uom_product_variant_ids?
            $field = $arch.find("field[name='secondary_uom_product_variant_ids']");
            if (!$field.length) {
                $("<FIELD/>", {
                    name: "secondary_uom_product_variant_ids",
                    invisible: 1,
                    modifiers: '{"invisible": true, "readonly": true}',
                }).prependTo($arch);
            }

            viewInfo.viewFields.order_line.views.form.arch = $arch[0].outerHTML;
        },
    });
});
