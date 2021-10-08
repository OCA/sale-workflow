/* Copyright 2021 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("sale_pwa_cache.PWA.managers.Sync", function(require) {
    "use strict";

    const SWSyncManager = require("web_pwa_cache.PWA.managers.Sync");
    const rpc = require("web_pwa_cache.PWA.core.base.rpc");

    /**
     * This class is used to manage sync operations
     */
    SWSyncManager.include({
        /**
         *
         * @param {Object} record
         * @param {Array} records_done
         * @returns {Promise}
         */
        _canSaleOrderBeConfirmed: function(record, records_done) {
            return new Promise(async (resolve, reject) => {
                const rid = record.args[0].id;
                try {
                    for (const sync_record of records_done) {
                        if (sync_record.model !== "sale.order.line") {
                            continue;
                        }
                        let aid = false;
                        if (sync_record.method === "create") {
                            aid = sync_record.args[0].id;
                        } else if (sync_record.method === "write") {
                            aid = sync_record.args[0][0];
                        } else if (sync_record.method === "unlink") {
                            aid = sync_record.args[0][0][0];
                        }
                        if (aid) {
                            const rec_line = await this._db.browse(
                                sync_record.model,
                                aid
                            );
                            if (
                                !_.isEmpty(rec_line) &&
                                rec_line.order_id === rid &&
                                sync_record.failed
                            ) {
                                return reject();
                            }
                        }
                    }
                } catch (err) {
                    return reject(err);
                }
                return resolve();
            });
        },

        /**
         * @override
         */
        onSynchronizedRecords: function(records_done) {
            if (!this.getParent()._isSaleAutoConfirm) {
                return this._super.apply(this, arguments);
            }
            return Promise.all([
                this._super.apply(this, arguments),
                new Promise(async (resolve, reject) => {
                    const error_sale_ids = [];
                    for (const record of records_done) {
                        if (
                            record.method !== "create" ||
                            record.model !== "sale.order"
                        ) {
                            continue;
                        }
                        const rid = record.args[0].id;
                        try {
                            await this._canSaleOrderBeConfirmed(record, records_done);
                        } catch (err) {
                            this._sendRecordFailToPages(
                                record.id,
                                `Can't confirm this sale order due to errors in the lines to synchronize. The record ID is ${rid}`
                            );
                            error_sale_ids.push(rid);
                            continue;
                        }
                        let has_errors = false;
                        try {
                            const [response] = await rpc.callJSonRpc(
                                "sale.order",
                                "action_confirm",
                                [rid]
                            );
                            const result = (await response.json()).result;
                            if (result !== true) {
                                has_errors = true;
                                error_sale_ids.push(rid);
                            }
                        } catch (err) {
                            has_errors = true;
                            error_sale_ids.push(rid);
                        }
                        if (has_errors) {
                            this._sendRecordFailToPages(
                                record.id,
                                `Can't confirm this sale order! The record ID is ${rid}`
                            );
                        }
                    }
                    if (!_.isEmpty(error_sale_ids)) {
                        return reject(
                            `Can't confirm all sale orders! Please, review them manually: ${error_sale_ids.join(
                                ", "
                            )}`
                        );
                    }
                    return resolve();
                }),
            ]);
        },
    });
});
