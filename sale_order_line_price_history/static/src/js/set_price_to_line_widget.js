/* Copyright 2023 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
 */
odoo.define(
    "sale_order_line_price_history.set_price_to_line_widget",
    function (require) {
        "use strict";

        var Widget = require("web.Widget");
        var widget_registry = require("web.widget_registry");

        var SetPriceToLineWidget = Widget.extend({
            template: "sale_order_line_price_history.set_price_to_line_widget",
            events: _.extend({}, Widget.prototype.events, {
                "click .set_price_to_line": "_onClickSetPrice",
            }),
            init: function (parent, record) {
                this.record = record;
                this._super(...arguments);
            },
            _onClickSetPrice: function () {
                this.do_action({
                    type: "ir.actions.act_window_close",
                    infos: {
                        price: this.record.data.price_unit,
                        discount: this.record.data.discount,
                    },
                });
            },
        });

        widget_registry.add("set_price_to_line", SetPriceToLineWidget);

        return SetPriceToLineWidget;
    }
);
