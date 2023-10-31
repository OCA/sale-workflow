odoo.define(
    "sale_order_lot_selection_by_quant.SaleOrderLotSelectByQuantListController",
    function (require) {
        "use strict";

        var ListController = require("web.ListController");
        var SaleOrderLotSelectByQuantListController = ListController.extend({
            /**
             * Intercepts the 'open_record' event.
             * Close the popup, passing down the information about the
             * selected lot_id
             *
             * @private
             * @param {OdooEvent} ev
             */
            _onOpenRecord: function (ev) {
                const selected = this.model.get(ev.data.id, {raw: true});
                const lot_id = selected.data.lot_id;
                this.do_action({
                    type: "ir.actions.act_window_close",
                    infos: {
                        changes: {
                            lot_id: {id: lot_id},
                        },
                    },
                });
            },
        });

        return SaleOrderLotSelectByQuantListController;
    }
);
