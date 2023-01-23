odoo.define(
    "sale_order_product_recommendation.section_and_note_backend",
    function (require) {
        "use strict";
        var ListRenderer = require("web.ListRenderer");
        const Context = require("web.Context");

        ListRenderer.include({
            _onAddRecord: function (ev) {
                var ctx = new Context(ev.currentTarget.dataset.context).eval();
                if (
                    typeof ctx.open_product_recommendation !== "undefined" &&
                    ctx.open_product_recommendation === true
                ) {
                    var saleOrderForm =
                        this.getParent() && this.getParent().getParent();
                    var $btn =
                        saleOrderForm &&
                        saleOrderForm.$el.find(
                            "button[name='action_sale_order_product_recommendation_wiz']"
                        );
                    if ($btn) {
                        $btn.trigger("click");
                    }
                } else {
                    this._super.apply(this, arguments);
                }
            },
        });
    }
);
