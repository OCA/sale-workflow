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

        A supplierinfo of a variant only brings that variant, while one without
        variant brings every variant of its template, the same rows
        ``_prepare_sellers()`` shows on each card.
        """
        groups = self.env["product.supplierinfo"]._read_group(
            [
                ("company_id", "in", [False, self.env.company.id]),
                ("partner_id.active", "=", True),
            ],
            groupby=["product_tmpl_id", "product_id"],
        )
        template_ids = [template.id for template, variant in groups if not variant]
        variant_ids = [variant.id for _template, variant in groups if variant]
        products = self.search(
            [
                ("sale_ok", "=", True),
                "|",
                ("product_tmpl_id", "in", template_ids),
                ("id", "in", variant_ids),
            ]
        )

        def sort_key(product):
            # ``_prepare_sellers()`` is ordered by ``sequence, min_qty desc,
            # price`` so the first record is the preferred vendor of this
            # variant. Cluster the products of the same vendor together and
            # keep the vendor priority.
            seller = product._prepare_sellers()[:1]
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
            # The context is propagated, so only honour the pinned row when it
            # belongs to this product.
            seller = self.env["product.supplierinfo"].browse(force_supplierinfo_item_id)
            if seller.product_tmpl_id == self.product_tmpl_id and (
                not seller.product_id or seller.product_id == self
            ):
                return seller
        return super()._select_seller(
            partner_id=partner_id,
            quantity=quantity,
            date=date,
            uom_id=uom_id,
            ordered_by=ordered_by,
            params=params,
        )
