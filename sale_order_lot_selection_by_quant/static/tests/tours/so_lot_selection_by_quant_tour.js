odoo.define(
    "sale_order_lot_selection_by_quant.tour.test_SO_lot_selection_by_quant",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        tour.register(
            "test_SO_lot_selection_by_quant",
            {
                test: true,
                url: "/web",
            },
            [
                tour.stepUtils.showAppsMenuItem(),
                {
                    content: "Navigate to the sale app",
                    trigger: ".o_app[data-menu-xmlid='sale.sale_menu_root']",
                },
                {
                    content: "Navigate to the existing order",
                    trigger: ".o_content table tbody tr td:contains('TESTSOLQUANT')",
                },
                {
                    content: "Click the edit button",
                    trigger: "div[role='toolbar'] .o_form_button_edit",
                },
                {
                    // TODO: How to make sure page has finished loading/updating
                    // without this ugly 3s wait?
                    content: "Wait for page to update",
                    trigger: "div",
                    run: function () {
                        return new Promise((resolve) => setTimeout(resolve, 3000));
                    },
                },
                {
                    content: "Click the sale order line",
                    trigger: ".o_notebook table td:contains('Cable Management Box')",
                },
                {
                    content:
                        "Click on the button on the order line (has to work on both tree and form)",
                    trigger: "table td button.o_select_lot_by_quant",
                },
                {
                    content: "Select the quant",
                    trigger: "table tbody tr td[title='TEST-LOT']",
                    extra_trigger: ".modal.show",
                },
                {
                    // TODO: How to make sure page has finished loading/updating
                    // without this ugly 3s wait?
                    content:
                        "Wait for page to update. If in form view, close the modal.",
                    trigger: "div",
                    run: function () {
                        new Promise((resolve) => setTimeout(resolve, 3000));
                        const btn = $(".modal-footer .btn-primary:contains('Save')");
                        if (btn.length > 0) {
                            btn.click();
                        }
                    },
                },
                {
                    content: "Click the save button",
                    trigger: "div[role='toolbar'] .o_form_button_save",
                },
                {
                    // TODO: How to make sure page has finished loading/updating
                    // without this ugly 3s wait?
                    content: "Wait for page to update",
                    trigger: "div",
                    run: function () {
                        return new Promise((resolve) => setTimeout(resolve, 3000));
                    },
                },
                {
                    content: "Check that the lot has been selected",
                    run: function () {}, // eslint-disable-line no-empty-function
                    trigger: ".o_select_lot_by_quant_cell:contains('TEST-LOT')",
                    extra_trigger: 'div[name="order_line"]',
                },
            ]
        );
    }
);
