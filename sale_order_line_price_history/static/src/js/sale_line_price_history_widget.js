/* Copyright 2021 Tecnativa - David Vidal
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
 */
odoo.define("sale_order_line_price_history.price_history_widget", function(require) {
    "use strict";

    var Widget = require("web.Widget");
    var widget_registry = require("web.widget_registry");

    var SaleOrderLinePriceHistoryWidget = Widget.extend({
        template: "sale_order_line_price_history.price_history_widget",
        events: _.extend({}, Widget.prototype.events, {
            "click .price_history": "_onClickButton",
        }),

        init: function(parent, params) {
            this.data = params.data;
            this._super(parent);
        },

        updateState: function(state) {
            var candidate = state.data[this.getParent().currentRow];
            if (candidate) {
                this.data = candidate.data;
                this.renderElement();
            }
        },

        _onClickButton: function() {
            // When it's a new line, we can't rely on a line id for the wizard, but
            // we can provide the proper element to find the historic lines.
            this.$el.find(".price_history").prop("special_click", true);
            var additional_context = {};
            if (this.data.id) {
                additional_context = {active_id: this.data.id};
            } else {
                var form_fields = this.getParent()
                    .getParent()
                    .getParent()
                    .getChildren();
                var partner_field = form_fields.filter(obj => {
                    return obj.name === "partner_id";
                })[0];
                additional_context = {
                    default_partner_id:
                        (partner_field && partner_field.value.data.id) ||
                        (this.data.order_partner_id &&
                            this.data.order_partner_id.res_id) ||
                        false,
                    default_product_id: this.data.product_id.res_id,
                };
            }
            this.do_action(
                "sale_order_line_price_history.sale_order_line_price_history_action",
                {
                    additional_context: additional_context,
                }
            );
        },
    });

    widget_registry.add(
        "sale_line_price_history_widget",
        SaleOrderLinePriceHistoryWidget
    );

    return SaleOrderLinePriceHistoryWidget;
});
