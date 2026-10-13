/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {ProductCatalogKanbanRecord} from "@product/product_catalog/kanban_record";
import {patch} from "@web/core/utils/patch";

patch(ProductCatalogKanbanRecord.prototype, {
    _getUpdateQuantityAndGetPriceParams() {
        const params = super._getUpdateQuantityAndGetPriceParams();
        // For a vendor card (supplier origin) send the vendor and the exact
        // supplierinfo it shows so the backend matches/creates the order line
        // for this precise card - a vendor can have several concurrently
        // valid cards (one per product.supplierinfo row), so vendor_id alone
        // cannot tell them apart. The new line form opened from the card gets
        // them too (see sale.order._get_catalog_new_line_vals).
        const {vendorId, supplierinfoId} = this.props.record.productCatalogData;
        if (vendorId) {
            params.vendor_id = vendorId;
        }
        if (supplierinfoId) {
            params.supplierinfo_id = supplierinfoId;
        }
        return params;
    },
});
