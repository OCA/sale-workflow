# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_applicable_rules(self, products, date, **kwargs):
        """Break the base=supplierinfo / base=standard_price tie in favor of
        the vendor's price when one is forced through the catalog.

        Both bases are otherwise equally applicable, so the plain
        ``product.pricelist.item`` ``_order`` (ending in ``id desc``) decides
        which one wins whenever a category or product has one rule of each -
        a common setup to offer a generic (cost-based) price with a
        vendor-specific (supplierinfo-based) override. That tie-break has no
        notion of "a vendor was requested", so ``force_filter_supplier_id``
        had no effect on which rule matched - only on the price a
        supplierinfo rule computed once it *did* match.

        ``force_filter_supplier_id`` is read off ``products`` (whichever
        product ``_compute_price_rule``/``_get_product_price`` were called
        with), never off ``self`` (the pricelist): every caller in this
        codebase - ``product_pricelist_supplierinfo`` itself,
        ``sale_order_line._get_product_price_context()``, this module's own
        catalog card pricing - annotates the *product*'s context, never the
        pricelist's, and core's own ``sale.order.line._compute_pricelist_item_id``
        calls ``pricelist_id._get_product_rule(product_id, ...)`` on a bare,
        uncontextualized pricelist. Checking ``self.env.context`` here would
        silently never match in real calls, even though the exact same check
        looks correct in isolation.

        Softly depends on ``product_pricelist_supplierinfo`` (no hard
        dependency, same as the rest of this module): the reordering is a
        no-op when there is no ``base == "supplierinfo"`` rule to move. It is
        nonetheless listed as a real dependency in the manifest, mainly so
        that this behaviour is actually exercised by this module's own
        tests instead of silently being a no-op in them too.
        """
        items = super()._get_applicable_rules(products, date, **kwargs)
        context = self.env.context
        if not context.get("force_filter_supplier_id") and products:
            context = products[:1].env.context
        if context.get("force_filter_supplier_id", False):
            # Vendor forced: try the vendor-specific rule(s) first.
            return items.sorted(lambda ppi: ppi.base != "supplierinfo")
        # No vendor forced: fall back to the generic rule(s) first.
        return items.sorted(lambda ppi: ppi.base == "supplierinfo")
