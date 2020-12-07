// Copyright 2020 Tecnativa - Alexandre Díaz
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
odoo.define("sale_web_pwa_cache_secondary_unit.AbstractView", function (require) {
    "use strict";

    var AbstractView = require("web.AbstractView");
    require("web_widget_one2many_product_picker_sale_secondary_unit.AbstractView");

    /**
     * This is pure hard-coded magic. Adds new fields to the widget form view.
     */
    AbstractView.include({
        /**
         * @private
         * @param {Object} viewInfo
         */
        _injectSaleSecondaryUnitFields: function (viewInfo) {
            this._super.apply(this, arguments);
            var $arch = $(viewInfo.viewFields.order_line.views.form.arch);
            // Modify secondary_uom_id
            var $field = $arch.find("field[name='secondary_uom_id']");
            if ($field.length) {
                $field.attr(
                    "t-attf-domain",
                    "[['product_variant_ids', 'in', [{{record_search.id}}]]]");
            }
            viewInfo.viewFields.order_line.views.form.arch = $arch[0].outerHTML;
        }
    });
});
