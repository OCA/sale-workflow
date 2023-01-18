/* Copyright 2021 Tecnativa - David Vidal
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
 */
odoo.define(
    "sale_order_product_recommendation.add_sale_line_widget",
    function (require) {
        "use strict";

        var Widget = require("web.Widget");
        var widget_registry = require("web.widget_registry");
        const session = require("web.session");

        var SaleRecommendationLineAddSaleLineWidget = Widget.extend({
            template: "sale_order_product_recommendation.add_sale_line_widget",
            events: _.extend({}, Widget.prototype.events, {
                "click .add_sale_line": "_onClickButton",
            }),

            init: function (parent, params) {
                this.data = params.data;
                this._super(parent);
            },

            updateState: function (state) {
                var candidate = state.data[this.getParent().currentRow];
                if (candidate) {
                    this.data = candidate.data;
                    this.renderElement();
                }
            },

            _onClickButton: function () {
                this.$el.find(".add_sale_line").prop("special_click", true);
                var ctx = Object.assign(session.user_context, {
                    default_product_id: this.data.product_id.res_id,
                    default_order_id: this.data.order_id.data.id,
                    bypass_action_accept: true,
                });
                this._rpc({
                    method: "new_sale_line",
                    model: "sale.order.recommendation.line",
                    args: [[this.id]],
                    context: ctx,
                }).then((res) => {
                    if (res) {
                        $("button[name='action_dummy_accept']").trigger("click");
                    }
                });
            },
        });

        widget_registry.add(
            "sale_order_product_recommendation_add_sale_line_widget",
            SaleRecommendationLineAddSaleLineWidget
        );

        return SaleRecommendationLineAddSaleLineWidget;
    }
);
