import {describe, expect, test} from "@odoo/hoot";
import {PriceHistoryWidget} from "@sale_order_line_price_history/js/sale_line_price_history_widget.esm";

function openPriceHistory({qtyInvoiced}) {
    const lineUpdates = [];
    const record = {
        data: {
            product_id: [1, "Product"],
            order_partner_id: [1, "Customer"],
            qty_invoiced: qtyInvoiced,
        },
        update: (value) => lineUpdates.push(value),
    };
    let options = null;
    PriceHistoryWidget.prototype.viewPriceHistory.call({
        props: {record, value: 1},
        actionService: {
            doAction: (action, actionOptions) => {
                options = actionOptions;
            },
        },
    });
    return {
        isViewOnly: options.additionalContext.price_history_readonly,
        lineUpdates,
        choosePrice: (price) => options.onClose(price),
        close: () => options.onClose(),
        invoiceLine: () => {
            record.data.qty_invoiced = 1;
        },
    };
}

describe("Viewing a customer's price history", () => {
    test("An uninvoiced line can use a historical price and discount", () => {
        // Given an uninvoiced sales order line
        const history = openPriceHistory({qtyInvoiced: 0});
        const price = {price_unit: 42, discount: 5};
        // When the user chooses a historical price and discount
        history.choosePrice(price);
        // Then the chosen values are applied to the line
        expect(history.isViewOnly).toBe(false);
        expect(history.lineUpdates).toEqual([price]);
    });
    test("An invoiced line opens history in view-only mode and cannot apply a price", () => {
        // Given an invoiced sales order line
        const history = openPriceHistory({qtyInvoiced: 1});
        // When a historical price is returned despite view-only mode
        history.choosePrice({price_unit: 42, discount: 5});
        // Then history is view-only and the line remains unchanged
        expect(history.isViewOnly).toBe(true);
        expect(history.lineUpdates).toEqual([]);
    });
    test("A line with a negative invoiced quantity cannot apply a price", () => {
        // Given a line with a negative invoiced quantity
        const history = openPriceHistory({qtyInvoiced: -1});
        // When a historical price is returned
        history.choosePrice({price_unit: 42, discount: 5});
        // Then history is view-only and the line remains unchanged
        expect(history.isViewOnly).toBe(true);
        expect(history.lineUpdates).toEqual([]);
    });
    test("A line invoiced while history is open cannot apply a price", () => {
        // Given history opened for an uninvoiced line
        const history = openPriceHistory({qtyInvoiced: 0});
        expect(history.isViewOnly).toBe(false);
        // When the line is invoiced before a historical price is chosen
        history.invoiceLine();
        history.choosePrice({price_unit: 42, discount: 5});
        // Then the line remains unchanged
        expect(history.lineUpdates).toEqual([]);
    });
    test("Closing history without choosing a price leaves the line unchanged", () => {
        // Given history opened for an uninvoiced line
        const history = openPriceHistory({qtyInvoiced: 0});
        // When the user closes history without selecting a price
        history.close();
        // Then the line remains unchanged
        expect(history.lineUpdates).toEqual([]);
    });
});
