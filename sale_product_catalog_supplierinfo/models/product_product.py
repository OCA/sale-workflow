# Copyright 2026 Tecnativa - Carlos Roca
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
