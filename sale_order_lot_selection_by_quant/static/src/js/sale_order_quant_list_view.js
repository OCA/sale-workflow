odoo.define("sale_order_lot_selection_by_quant.SaleOrderQuantListView", function (
    require
) {
    "use strict";

    var ListView = require("web.ListView");
    var SaleOrderLotSelectByQuantListController = require("sale_order_lot_selection_by_quant.SaleOrderLotSelectByQuantListController");
    var viewRegistry = require("web.view_registry");

    var SaleOrderQuantListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: SaleOrderLotSelectByQuantListController,
        }),
    });

    viewRegistry.add("sale_order_lot_selection_by_quant", SaleOrderQuantListView);

    return SaleOrderQuantListView;
});
