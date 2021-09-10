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
                            const [response] = await rpc.callJSonRpc(
                                "sale.order",
                                "action_confirm",
                                [rid]
                            );
                            const result = (await response.json()).result;
                            if (result !== true) {
                                error_sale_ids.push(rid);
                            }
                        } catch (err) {
                            error_sale_ids.push(rid);
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
