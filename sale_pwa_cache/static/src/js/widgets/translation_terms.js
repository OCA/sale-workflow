// Copyright 2022 Tecnativa - Alexandre Díaz
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
odoo.define("web_pwa_cache_sales.FieldOne2ManyProductPickerTranslationTerms", function(
    require
) {
    "use strict";

    var _t = require("web.core")._t;

    // Workaround to force translations of type "openerp-web".
    // This is necessary because Odoo doesn't support translations on xml attributes.
    // Note that the product_picker module has implemented the use of "_('')"
    // in the xml attributes to translate the terms (in the client side). These method
    // uses the translations loaded here:
    _t("Contains");
    _t("Starts With");
    _t("Category");
    _t("History");
    _t("History (Shipping)");
});
