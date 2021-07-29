/* Copyright 2021 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("sale_pwa_cache.PWA.systems.Database", function(require) {
    "use strict";

    const DatabaseSystem = require("web_pwa_cache.PWA.systems.Database");

    DatabaseSystem.include({
        _searchables: _.deepExtend({}, DatabaseSystem.prototype._searchables, {
            "product.product": {
                sale_order_partner_id_product: "_compute_sale_order_partner_id_product",
            },
        }),

        _compute_sale_order_partner_id_product: function(operator, value, context) {
            return new Promise(async (resolve, reject) => {
                let partner_id = false;
                let partner = false;
                try {
                    if (
                        context.active_search_group_name === "product_history_shipping"
                    ) {
                        partner_id = context.sale_order_partner_shipping_id;
                        partner = await this.browse("res.partner", partner_id);
                    } else {
                        partner_id = context.sale_order_partner_id;
                        partner = await this.browse("res.partner", partner_id);
                        partner = await this.browse(
                            "res.partner",
                            partner.commercial_partner_id &&
                                partner.commercial_partner_id[0]
                        );
                    }
                } catch (err) {
                    partner = false;
                }

                if (_.isEmpty(partner) || ["=", "!="].indexOf(operator) === -1) {
                    return resolve([]);
                }
                try {
                    const orders = await this.search_read(
                        "sale.order",
                        [
                            ["partner_id", "=", partner.id],
                            ["date_order", ">=", moment().subtract(13, "months")],
                        ],
                        undefined,
                        undefined,
                        undefined,
                        undefined,
                        context
                    );
                    if (_.isEmpty(orders)) {
                        return resolve([]);
                    }
                    const lines = await this.search_read(
                        "sale.order.line",
                        [
                            ["order_id", "in", this.ids(orders)],
                            ["state", "in", ["sale", "done"]],
                        ],
                        undefined,
                        ["product_id"],
                        undefined,
                        "id DESC, sequence DESC",
                        context
                    );

                    let products_domain = _.chain(lines)
                        .filter("product_id")
                        .map(line => line.product_id[0])
                        .value();
                    if (_.isEmpty(products_domain)) {
                        products_domain = [0];
                    }
                    return resolve([
                        ["id", operator == "=" ? "in" : "not in", products_domain],
                    ]);
                } catch (err) {
                    return reject(err);
                }
            });
        },
    });
});
