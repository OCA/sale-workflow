odoo.define("sale_order_discount_fast_change_id.SaleOrderView", function (require) {
    "use strict";

    const FormView = require("web.FormView");
    const viewRegistry = require("web.view_registry");

    // Do not register the discount wizard
    viewRegistry.add("sale_discount_form", FormView);

    return FormView;
});
