/* Copyright 2021 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("sale_pwa_cache.PWA", function(require) {
    "use strict";

    const PWA = require("web_pwa_oca.PWA");

    PWA.include({
        /**
         * @override
         */
        init: function(params) {
            this._super.apply(this, arguments);
            this._isSaleAutoConfirm = params.is_sale_auto_confirm;
        },
    });
});
