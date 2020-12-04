// Copyright 2020 Tecnativa - Alexandre Díaz
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
odoo.define("web_pwa_cache_sales.FieldOne2ManyProductPicker", function (
    require
) {
    "use strict";

    var FieldOne2ManyProductPicker = require("web_widget_one2many_product_picker.FieldOne2ManyProductPicker");

    FieldOne2ManyProductPicker.include({
        search_read_fields: _.union(FieldOne2ManyProductPicker.prototype.search_read_fields, [
            "uom_category_id",
        ]),
    });
});
