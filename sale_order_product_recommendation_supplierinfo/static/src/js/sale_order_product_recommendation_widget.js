/* Copyright 2021 Tecnativa - David Vidal
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
 */
odoo.define(
    "sale_order_product_recommendation_supplierinfo.add_sale_line_widget",
    function (require) {
        "use strict";

        var SaleRecommendationLineAddSaleLineWidget = require("sale_order_product_recommendation.add_sale_line_widget");

        SaleRecommendationLineAddSaleLineWidget.include({
            _setOrderLineContext: function () {
                var ctx = this._super.apply(this, arguments);
                ctx = Object.assign(ctx, {
                    default_vendor_id: this.data.vendor_id.res_id,
                    default_vendor_comment: this.data.vendor_comment,
                });
                return ctx;
            },
        });
    }
);
