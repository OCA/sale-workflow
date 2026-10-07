# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _get_procurements_to_merge_groupby(self, procurement):
        """Never merge procurements pinned to a different supplierinfo.

        Core only groups procurements bound for the same purchase order line
        by ``(product, uom, ...)``, with no notion of price/vendor row: two
        sale lines of the SAME vendor but pinned to different concurrently
        valid ``product.supplierinfo`` rows (see
        ``sale.order.line.supplierinfo_id``'s docstring - a real, confirmed
        case for this catalog's own vendor cards, one per row) would
        otherwise be merged into a single purchase order line, summing their
        quantity and silently keeping only one of the two prices - the exact
        same "different price, only one wins" collapsing this module's
        catalog card split exists to avoid, just one step further down the
        sale-to-purchase chain.
        """
        supplierinfo = procurement.values.get("supplierinfo_id")
        return super()._get_procurements_to_merge_groupby(procurement) + (
            supplierinfo.id if supplierinfo else False,
        )

    def _update_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, line
    ):
        """Keep the price of the pinned supplierinfo when a procurement is
        merged into an existing line, instead of the one core's _select_seller()
        would re-derive for the new total quantity from the vendor alone.

        The procurements of different rows of the same vendor are kept in
        different lines within a run by ``_get_procurements_to_merge_groupby``
        and across runs by their vendor comment
        (procurement_purchase_no_grouping_comment), so the merged line is the
        one of the same row.
        """
        supplierinfo = values.get("supplierinfo_id")
        if supplierinfo:
            product_id = product_id.with_context(
                force_supplierinfo_item_id=supplierinfo.id
            )
        return super()._update_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, line
        )
