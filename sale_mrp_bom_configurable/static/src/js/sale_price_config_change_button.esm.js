/** @odoo-module */
import {ListController} from "@web/views/list/list_controller";
import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";

export class SalePriceController extends ListController {
    setup() {
        super.setup();
    }
    OnTestClick() {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "wizard.sale.price.config.change",
            name: "Price change",
            view_mode: "form",
            view_type: "form",
            views: [[false, "form"]],
            target: "new",
            res_id: false,
        });
    }
}

registry.category("views").add("sale_price_button", {
    ...listView,
    Controller: SalePriceController,
    buttonTemplate: "button_sale.ListView.Buttons",
});
