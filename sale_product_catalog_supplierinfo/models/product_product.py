# Copyright 2026 Tecnativa - Carlos Roca
# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # New catalog origin added on top of the ones defined in
    # ``sale_product_catalog_extended``. Like the others, it is a display-only
    # search panel field whose actual product restriction is resolved through
    # the matching ``_get_product_picker_data_<key>`` method.
    catalog_origin_data = fields.Selection(
        selection_add=[("supplierinfo", "Suppliers")],
    )

    @api.model
    def _get_product_picker_data_supplierinfo(self):
        """Return the ordered product ids for the ``supplierinfo`` catalog
        origin: every sellable product that has at least one vendor, grouped by
        its preferred vendor and ordered by the supplierinfo sequence.
        """
        products = self.search([("sale_ok", "=", True), ("seller_ids", "!=", False)])

        def sort_key(product):
            # ``seller_ids`` is already ordered by ``sequence, min_qty desc,
            # price`` so the first record is the preferred vendor. Cluster the
            # products of the same vendor together and keep the vendor priority.
            seller = product.seller_ids[:1]
            return (
                seller.partner_id.id if seller else 0,
                seller.sequence if seller else 9999,
                product.id,
            )

        return products.sorted(sort_key).ids

    def _select_seller(
        self,
        partner_id=False,
        quantity=0.0,
        date=None,
        uom_id=False,
        ordered_by="price_discounted",
        params=False,
    ):
        """Let a caller pin one exact ``product.supplierinfo`` record instead
        of having it re-resolved by partner/quantity/date.

        Needed once a specific row was already chosen for the line (the
        catalog vendor card, or a manually picked ``supplierinfo_id``):
        without it, a vendor with several concurrently valid rows (e.g. one
        price about to expire and its replacement already active) could have
        the *wrong* one re-selected downstream - typically on the purchase
        order line generated from the sale line's procurement, since that
        only carries the vendor, not the exact row.
        """
        force_supplierinfo_item_id = self.env.context.get(
            "force_supplierinfo_item_id", False
        )
        if force_supplierinfo_item_id:
            return self.env["product.supplierinfo"].browse(force_supplierinfo_item_id)
        return super()._select_seller(
            partner_id=partner_id,
            quantity=quantity,
            date=date,
            uom_id=uom_id,
            ordered_by=ordered_by,
            params=params,
        )
