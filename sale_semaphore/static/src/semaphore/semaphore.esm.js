/** @odoo-module **/

import relational_fields from "web.relational_fields";
import fieldRegistry from "web.field_registry";
import rpc from "web.rpc";
import core from "web.core";
const QWeb = core.qweb;
const _t = core._t;
import {formatMonetary} from "@web/fields/formatters";

export const Semaphore = relational_fields.FieldSelection.extend({
    _getSupportedModels: function () {
        return ["sale.order.line"];
    },
    _renderEdit: function () {
        this._renderReadonly();
    },
    _renderReadonly: function () {
        this._super.apply(this, arguments);
        const value = this.recordData.semaphore_active ? this.value : "dark";
        this.$el.addClass("text-" + value);
        this.$el.attr("tabindex", "0");
        this.$el.on("click", (ev) => {
            ev.preventDefault();
            ev.stopPropagation();
            if (!this._getSupportedModels().includes(this.model)) {
                this.displayNotification({
                    message: _t(
                        "The semaphore assignation does not work in this model."
                    ),
                    type: "info",
                });
                return;
            }
            if (!this.recordData.semaphore_active) {
                this.displayNotification({
                    message: _t(
                        "The product or its category has not the semaphore activated."
                    ),
                    type: "info",
                });
                return;
            }
            this.initPopover();
            this.$el.focus();
        });
        // When doing focusout destroy the popover to refresh the data
        this.$el.on("focusout", () => {
            if (!this.recordData.semaphore_active) {
                return;
            }
            setTimeout(() => {
                this.$el.popover("dispose");
            }, 150);
        });
    },
    initPopover: function () {
        var max_price_success = formatMonetary(
            this.recordData.semaphore_max_price_success,
            {
                data: this.recordData,
                currencyField: "currency_id",
            }
        );
        var max_price_warning = formatMonetary(
            this.recordData.semaphore_max_price_warning,
            {
                data: this.recordData,
                currencyField: "currency_id",
            }
        );
        var max_price_danger = formatMonetary(
            this.recordData.semaphore_max_price_danger,
            {
                data: this.recordData,
                currencyField: "currency_id",
            }
        );
        const $content = $(
            QWeb.render("sale_semaphore.SemaphorePopover", {
                data: {
                    max_price_success,
                    max_price_warning,
                    max_price_danger,
                },
            })
        );
        $content
            .on("click", ".set_price_success", () => {
                this.trigger_up("field_changed", {
                    dataPointID: this.record.id,
                    changes: {
                        price_unit: this.recordData.semaphore_max_price_success,
                        discount: 0,
                    },
                    onSuccess: () => {
                        const $tr = this.$el.closest("tr");
                        $tr.find("td[name='price_unit']").text(
                            formatMonetary(
                                this.recordData.semaphore_max_price_success,
                                {
                                    data: this.recordData,
                                    currencyField: "currency_id",
                                    noSymbol: true,
                                }
                            )
                        );
                        $tr.find("td[name='discount']").text(
                            formatMonetary(0, {
                                data: this.recordData,
                                currencyField: "currency_id",
                                noSymbol: true,
                            })
                        );
                    },
                });
            })
            .on("click", ".set_price_warning", () => {
                this.trigger_up("field_changed", {
                    dataPointID: this.record.id,
                    changes: {
                        price_unit: this.recordData.semaphore_max_price_warning,
                        discount: 0,
                    },
                    onSuccess: () => {
                        const $tr = this.$el.closest("tr");
                        $tr.find("td[name='price_unit']").text(
                            formatMonetary(
                                this.recordData.semaphore_max_price_warning,
                                {
                                    data: this.recordData,
                                    currencyField: "currency_id",
                                    noSymbol: true,
                                }
                            )
                        );
                        $tr.find("td[name='discount']").text(
                            formatMonetary(0, {
                                data: this.recordData,
                                currencyField: "currency_id",
                                noSymbol: true,
                            })
                        );
                    },
                });
            })
            .on("click", ".set_price_danger", () => {
                this.trigger_up("field_changed", {
                    dataPointID: this.record.id,
                    changes: {
                        price_unit: this.recordData.semaphore_max_price_danger,
                        discount: 0,
                    },
                    onSuccess: () => {
                        const $tr = this.$el.closest("tr");
                        $tr.find("td[name='price_unit']").text(
                            formatMonetary(this.recordData.semaphore_max_price_danger, {
                                data: this.recordData,
                                currencyField: "currency_id",
                                noSymbol: true,
                            })
                        );
                        $tr.find("td[name='discount']").text(
                            formatMonetary(0, {
                                data: this.recordData,
                                currencyField: "currency_id",
                                noSymbol: true,
                            })
                        );
                    },
                });
            })
            .on("click", ".reset_value", async () => {
                if (!this.record.res_id) {
                    this.displayNotification({
                        message: _t("Please save to be able to reset the price."),
                        type: "danger",
                    });
                    return;
                }
                const price_unit_val = await rpc.query({
                    model: this.model,
                    method: "get_reset_price_unit",
                    args: [this.record.res_id],
                });
                this.trigger_up("field_changed", {
                    dataPointID: this.record.id,
                    changes: {price_unit: price_unit_val, discount: 0},
                    onSuccess: () => {
                        const $tr = this.$el.closest("tr");
                        $tr.find("td[name='price_unit']").text(
                            formatMonetary(this.recordData.price_unit_val, {
                                data: this.recordData,
                                currencyField: "currency_id",
                                noSymbol: true,
                            })
                        );
                        $tr.find("td[name='discount']").text(
                            formatMonetary(0, {
                                data: this.recordData,
                                currencyField: "currency_id",
                                noSymbol: true,
                            })
                        );
                    },
                });
            });
        const options = {
            content: $content,
            html: true,
            placement: "left",
            title: _t("Semaphore"),
            trigger: "focus",
            delay: {show: 0, hide: 100},
        };
        this.$el.popover(options);
    },
});

fieldRegistry.add("semaphore", Semaphore);
