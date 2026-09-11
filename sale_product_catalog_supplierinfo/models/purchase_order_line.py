# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_purchase_order_line_from_procurement(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
        po,
    ):
        """Pin the exact supplierinfo the sale line resolved to, when known.

        ``sale.order.line._prepare_procurement_values()`` (this module) and
        ``sale_purchase_force_vendor`` both put a ``supplierinfo_id`` in
        ``values``, but nothing forwards it into ``_select_seller()`` for the
        line about to be created here - it silently falls back to a fresh
        partner/quantity/date match, which can pick a *different* row than
        the one shown/priced on the sale line when the vendor has more than
        one concurrently valid supplierinfo.
        """
        supplierinfo_id = values.get("supplierinfo_id")
        if supplierinfo_id:
            product_id = product_id.with_context(
                force_supplierinfo_item_id=supplierinfo_id.id
            )
        return super()._prepare_purchase_order_line_from_procurement(
            product_id,
            product_qty,
            product_uom,
            location_dest_id,
            name,
            origin,
            company_id,
            values,
            po,
        )
