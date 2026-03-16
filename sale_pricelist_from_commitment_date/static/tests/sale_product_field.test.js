import {describe, expect, test} from "@odoo/hoot";
import {SaleOrderLineProductField} from "@sale/js/sale_product_field";
import {serializeDateTime} from "@web/core/l10n/dates";

const {DateTime} = luxon;

function createMockContext(data) {
    return {
        props: {
            record: {
                model: {
                    root: {
                        data,
                    },
                },
            },
        },
        _getCommitmentDateSerialized:
            SaleOrderLineProductField.prototype._getCommitmentDateSerialized,
    };
}

function callMethod(methodName, context) {
    return SaleOrderLineProductField.prototype[methodName].call(context);
}

function createContextWithDates({commitmentDate, dateOrder = "2026-03-10T10:00:00"}) {
    return createMockContext({
        commitment_date: commitmentDate
            ? DateTime.fromISO(commitmentDate)
            : commitmentDate,
        date_order: DateTime.fromISO(dateOrder),
    });
}

describe("Sale Pricelist From Commitment Date", () => {
    // The actual patch is applied by importing the module above

    test("_getAdditionalDialogProps sets soDate and date from commitment_date", () => {
        const commitmentDate = "2026-03-20T10:00:00";
        const context = createContextWithDates({commitmentDate});
        const result = callMethod("_getAdditionalDialogProps", context);
        const expectedDate = serializeDateTime(DateTime.fromISO(commitmentDate));
        expect(result.soDate).toBe(expectedDate);
        expect(result.date).toBe(expectedDate);
    });

    test("_getAdditionalDialogProps does not override when commitment_date is null", () => {
        const context = createContextWithDates({commitmentDate: null});
        const result = callMethod("_getAdditionalDialogProps", context);
        expect(result.soDate).toBe(undefined);
        expect(result.date).toBe(undefined);
    });

    test("_getAdditionalRpcParams sets date from commitment_date", () => {
        const commitmentDate = "2026-03-20T10:00:00";
        const context = createContextWithDates({commitmentDate});
        const result = callMethod("_getAdditionalRpcParams", context);
        const expectedDate = serializeDateTime(DateTime.fromISO(commitmentDate));
        expect(result.date).toBe(expectedDate);
    });

    test("_getAdditionalRpcParams does not override when commitment_date is null", () => {
        const context = createContextWithDates({commitmentDate: null});
        const result = callMethod("_getAdditionalRpcParams", context);
        expect(result.date).toBe(undefined);
    });

    test("commitment_date takes precedence over date_order", () => {
        const commitmentDate = "2026-03-20T10:00:00";
        const dateOrder = "2026-03-10T10:00:00";
        const context = createContextWithDates({commitmentDate, dateOrder});
        const dialogProps = callMethod("_getAdditionalDialogProps", context);
        const rpcParams = callMethod("_getAdditionalRpcParams", context);
        const expectedDate = serializeDateTime(DateTime.fromISO(commitmentDate));
        expect(dialogProps.soDate).toBe(expectedDate);
        expect(dialogProps.date).toBe(expectedDate);
        expect(rpcParams.date).toBe(expectedDate);
    });
});
